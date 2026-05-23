import hashlib
import json
import os
import yaml
from typing import List, Optional
from .models import Theory, KernelTheory, KernelManifest

class KernelManager:
    """
    Manages the protected seed set.
    Read-only at runtime. Verified on load.
    The closest approximation of F* the system has.
    """

    def __init__(self, kernel_dir: str):
        self.kernel_dir = kernel_dir
        self._theories: Optional[List[Theory]] = None
        self._manifest: Optional[KernelManifest] = None
        # We don't raise on first run if manifest is missing, we'll build it.
        if os.path.exists(os.path.join(self.kernel_dir, "manifest.json")):
            self._verify_kernel_integrity()
            self._manifest = self._load_manifest()

    def _verify_kernel_integrity(self):
        """
        Hash-verify the kernel on load.
        Raises if kernel has been modified at runtime.
        """
        manifest_path = os.path.join(self.kernel_dir, "manifest.json")
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)

        # Verify each theory file hash
        for kt_data in manifest_data.get("theories", []):
            theory_id = kt_data['theory']['id']
            theory_path = os.path.join(self.kernel_dir, f"{theory_id}.yaml")
            if os.path.exists(theory_path):
                actual_hash = self._compute_hash(theory_path)
                if actual_hash != kt_data.get("content_hash"):
                    raise RuntimeError(
                        f"KERNEL INTEGRITY VIOLATION: {theory_id} "
                        f"has been modified. The kernel is read-only. "
                        f"Expected {kt_data['content_hash']}, got {actual_hash}."
                    )

    def _compute_hash(self, path: str) -> str:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _load_manifest(self) -> Optional[KernelManifest]:
        manifest_path = os.path.join(self.kernel_dir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                data = json.load(f)
                return KernelManifest(
                    version=data["version"],
                    theories=[],  # loaded separately as full objects
                    manifest_hash=data["manifest_hash"],
                    primary_blueprints=data.get("primary_blueprints", []),
                    known_fstar_gaps=data.get("known_fstar_gaps", []),
                    curator_notes=data.get("curator_notes", "")
                )
        return None

    @property
    def theories(self) -> List[Theory]:
        if self._theories is None:
            self._theories = self._load_all()
        return self._theories

    def _load_all(self) -> List[Theory]:
        theories = []
        if not os.path.exists(self.kernel_dir):
            return []
        for fname in os.listdir(self.kernel_dir):
            if fname.endswith('.yaml'):
                with open(os.path.join(self.kernel_dir, fname), 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        theories.append(Theory(**data))
        return theories

    @property
    def blueprints(self) -> List[Theory]:
        return [t for t in self.theories
                if t.coverage and t.coverage.coverage_type == "blueprint"]

    def get_fstar_gaps(self) -> List[str]:
        """Return known gaps in F* coverage from manifest."""
        if self._manifest:
            return self._manifest.known_fstar_gaps
        return []
