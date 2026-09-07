import os
import sys
import glob
import subprocess
import shutil

class SystemAccess:
    """
    OS System & File Access Service for PROJECT AURA.
    Provides safe file search, document reading, and system settings inspection.
    """

    @staticmethod
    def get_user_directories():
        user_home = os.path.expanduser("~")
        return {
            "home": user_home,
            "downloads": os.path.join(user_home, "Downloads"),
            "documents": os.path.join(user_home, "Documents"),
            "desktop": os.path.join(user_home, "Desktop"),
            "pictures": os.path.join(user_home, "Pictures"),
            "workspace": os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        }

    @classmethod
    def search_files(cls, query: str, limit=5) -> dict:
        """Search files by pattern or keyword across User directories"""
        user_dirs = cls.get_user_directories()
        pattern = f"*{query.strip()}*"
        matches = []

        for dir_name, dir_path in user_dirs.items():
            if os.path.exists(dir_path):
                try:
                    for root, _, files in os.walk(dir_path):
                        for f in files:
                            if query.lower() in f.lower():
                                full_p = os.path.join(root, f)
                                matches.append({
                                    "filename": f,
                                    "path": full_p,
                                    "size_bytes": os.path.getsize(full_p),
                                    "folder": os.path.basename(root)
                                })
                                if len(matches) >= limit:
                                    break
                        if len(matches) >= limit:
                            break
                except Exception:
                    pass
            if len(matches) >= limit:
                break

        if matches:
            summary = f"Found {len(matches)} file(s) matching '{query}':\n"
            for m in matches:
                summary += f" • {m['filename']} (in {m['folder']}, {m['size_bytes']:,} bytes)\n"
            return {"success": True, "matches": matches, "text": summary.strip()}
        else:
            return {"success": False, "text": f"No files matching '{query}' were found in your documents or downloads."}

    @classmethod
    def read_file_preview(cls, file_name: str, max_chars=400) -> dict:
        """Finds and reads a text or code document preview"""
        res = cls.search_files(file_name, limit=1)
        if not res["success"] or not res["matches"]:
            return {"success": False, "text": f"Could not find document '{file_name}' to read."}

        target_path = res["matches"][0]["path"]
        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars)
            return {
                "success": True,
                "path": target_path,
                "text": f"Preview of '{os.path.basename(target_path)}':\n{content}..."
            }
        except Exception as e:
            return {"success": False, "text": f"Error reading '{file_name}': {e}"}

    @staticmethod
    def inspect_disk_space() -> dict:
        """Inspect storage drives and free space"""
        try:
            usage = shutil.disk_usage(os.path.expanduser("~"))
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent = (used_gb / total_gb) * 100
            return {
                "success": True,
                "total_gb": round(total_gb, 1),
                "used_gb": round(used_gb, 1),
                "free_gb": round(free_gb, 1),
                "percent_used": round(percent, 1),
                "text": f"Primary drive has {free_gb:.1f} GB free out of {total_gb:.1f} GB total ({percent:.1f}% used)."
            }
        except Exception:
            return {"success": False, "text": "Unable to inspect disk storage."}
