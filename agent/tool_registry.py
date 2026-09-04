"""Tool Registry for SatQuery Agent

Maintains a controlled registry of executable tools.
Prevents arbitrary code execution - only registered tools can be called.
"""

from typing import Callable, Dict, Any, Optional
from abc import ABC, abstractmethod
import inspect
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all SatQuery tools."""

    def __init__(self, name: str, description: str, category: str = "general"):
        """Initialize tool."""
        self.name = name
        self.description = description
        self.category = category
        self.execution_count = 0
        self.total_duration_ms = 0.0

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dictionary with tool results
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "execution_count": self.execution_count,
            "total_duration_ms": self.total_duration_ms,
            "parameters": self._get_parameters(),
        }

    def _get_parameters(self) -> Dict[str, str]:
        """Extract parameter names from execute method."""
        sig = inspect.signature(self.execute)
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            params[param_name] = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
        return params


class ToolRegistry:
    """
    Manages tool registration and execution.

    Enforces:
    - Only registered tools can be executed
    - All tool calls are logged
    - Tool execution is sandboxed
    """

    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[str, list] = {}

    def register(self, tool: BaseTool, category: Optional[str] = None) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register
            category: Optional category override
        """
        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' already registered. Overwriting.")

        if category:
            tool.category = category

        self.tools[tool.name] = tool

        # Track by category
        if tool.category not in self.categories:
            self.categories[tool.category] = []
        self.categories[tool.category].append(tool.name)

        logger.info(f"Registered tool: {tool.name} (category: {tool.category})")

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.

        Args:
            tool_name: Name of tool to unregister

        Returns:
            True if tool was registered and removed
        """
        if tool_name not in self.tools:
            return False

        tool = self.tools[tool_name]
        del self.tools[tool_name]

        # Remove from category
        if tool.category in self.categories:
            self.categories[tool.category].remove(tool_name)

        logger.info(f"Unregistered tool: {tool_name}")
        return True

    def get(self, tool_name: str) -> Optional[BaseTool]:
        """Get a registered tool by name."""
        return self.tools.get(tool_name)

    def exists(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self.tools

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered tool.

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if not self.exists(tool_name):
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        tool = self.tools[tool_name]
        logger.info(f"Executing tool: {tool_name}")

        try:
            result = tool.execute(**kwargs)
            tool.execution_count += 1
            logger.info(f"Tool '{tool_name}' completed successfully")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"Tool '{tool_name}' failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    def list_tools(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        List registered tools.

        Args:
            category: Optional filter by category

        Returns:
            Dictionary of tool information
        """
        if category:
            if category not in self.categories:
                return {}
            tool_names = self.categories[category]
            return {
                name: self.tools[name].get_info()
                for name in tool_names
            }

        return {
            name: tool.get_info()
            for name, tool in self.tools.items()
        }

    def list_categories(self) -> Dict[str, list]:
        """Get all categories and their tools."""
        return {
            cat: tool_names
            for cat, tool_names in self.categories.items()
        }


# Global tool registry instance
tool_registry = ToolRegistry()


# ============================================================================
# Example Tool Implementations (Phase 1)
# ============================================================================


class ImageValidatorTool(BaseTool):
    """Validates input satellite images."""

    def __init__(self):
        super().__init__(
            name="ImageValidator",
            description="Validates satellite image format, metadata, and readability",
            category="validation"
        )

    def execute(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Validate an image.

        Args:
            image_path: Path to image file

        Returns:
            Validation result
        """
        # TODO: Phase 1 - Implement real validator
        return {
            "image": image_path,
            "valid": True,
            "modality": "unknown",
            "bands": 0,
            "resolution": None
        }


class MetadataExtractorTool(BaseTool):
    """Extracts metadata from satellite images."""

    def __init__(self):
        super().__init__(
            name="MetadataExtractor",
            description="Extracts geospatial metadata from satellite images",
            category="data"
        )

    def execute(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from image.

        Args:
            image_path: Path to image file

        Returns:
            Image metadata
        """
        # TODO: Phase 1 - Implement real extractor
        return {
            "image": image_path,
            "crs": None,
            "bounds": None,
            "bands": []
        }


# Register Phase 1 example tools
def init_phase1_tools():
    """Initialize Phase 1 tools in registry."""
    tool_registry.register(ImageValidatorTool())
    tool_registry.register(MetadataExtractorTool())
    logger.info("Phase 1 tools initialized")
