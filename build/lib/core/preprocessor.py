import asyncio
import aiofiles
import tempfile
import os
import re

class CodePreprocessor:
    def __init__(self, code: str, file_path: str = None):
        self.code = code
        self.file_path = file_path

    async def process(self):
        normalized_code = self._normalize_code(self.code)
        language = self._detect_language()
        dependencies = self._detect_dependencies(normalized_code)
        
        temp_file_path = await self._create_temp_file(normalized_code)

        return {
            "normalized_code": normalized_code,
            "language": language,
            "dependencies": dependencies,
            "temp_file_path": temp_file_path,
            "total_lines": len(self.code.splitlines())
        }

    def _normalize_code(self, code: str) -> str:
        # Simple normalization: strip leading/trailing whitespace from each line
        return "\n".join([line.strip() for line in code.splitlines()])

    def _detect_language(self) -> str:
        if self.file_path and self.file_path.endswith(".py"):
            return "python"
        # Basic heuristic for Python
        if "import " in self.code or "def " in self.code or "class " in self.code:
            return "python"
        return "unknown"

    def _detect_dependencies(self, code: str) -> list:
        # Simple regex for import statements
        imports = re.findall(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", code, re.MULTILINE)
        return sorted(list(set(imports)))

    async def _create_temp_file(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".py", text=True)
        async with aiofiles.open(path, "w") as f:
            await f.write(content)
        os.close(fd)
        return path

    @staticmethod
    def cleanup_temp_file(path: str):
        if path and os.path.exists(path):
            os.remove(path)
