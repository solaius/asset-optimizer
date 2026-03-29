from pathlib import Path

from asset_optimizer.assets.base import AssetContent
from asset_optimizer.assets.image import ImageAssetType
from asset_optimizer.assets.prompt import PromptAssetType
from asset_optimizer.assets.registry import AssetRegistry
from asset_optimizer.assets.skill import SkillAssetType


class TestAssetContent:
    def test_text_content(self) -> None:
        content = AssetContent(text="Hello world")
        assert content.text == "Hello world"
        assert content.file_path is None

    def test_file_content(self) -> None:
        content = AssetContent(file_path=Path("/tmp/image.png"))
        assert content.text is None
        assert content.file_path == Path("/tmp/image.png")

    def test_metadata(self) -> None:
        content = AssetContent(text="test", metadata={"key": "value"})
        assert content.metadata["key"] == "value"


class TestPromptAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = PromptAssetType()
        assert asset_type.name == "prompt"
        assert ".txt" in asset_type.file_extensions
        assert ".md" in asset_type.file_extensions

    def test_load_and_save(self, tmp_path: Path) -> None:
        asset_type = PromptAssetType()
        path = tmp_path / "prompt.txt"
        path.write_text("You are a helpful assistant.")

        content = asset_type.load(path)
        assert content.text == "You are a helpful assistant."

        new_path = tmp_path / "prompt2.txt"
        asset_type.save(content, new_path)
        assert new_path.read_text() == "You are a helpful assistant."

    def test_validate_nonempty(self) -> None:
        asset_type = PromptAssetType()
        errors = asset_type.validate(AssetContent(text="Valid prompt"))
        assert errors == []

    def test_validate_empty(self) -> None:
        asset_type = PromptAssetType()
        errors = asset_type.validate(AssetContent(text=""))
        assert len(errors) > 0

    def test_render_for_prompt(self) -> None:
        asset_type = PromptAssetType()
        content = AssetContent(text="Test prompt")
        rendered = asset_type.render_for_prompt(content)
        assert "Test prompt" in rendered

    def test_default_evaluation(self) -> None:
        asset_type = PromptAssetType()
        eval_config = asset_type.default_evaluation()
        assert eval_config["asset_type"] == "prompt"
        assert len(eval_config["criteria"]) > 0


class TestSkillAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = SkillAssetType()
        assert asset_type.name == "skill"
        assert ".md" in asset_type.file_extensions

    def test_load_skill_with_frontmatter(self, tmp_path: Path) -> None:
        skill_content = (
            "---\nname: test-skill\ndescription: A test\n---\n\n"
            "# Skill Body\nDo things."
        )
        path = tmp_path / "skill.md"
        path.write_text(skill_content)

        asset_type = SkillAssetType()
        content = asset_type.load(path)
        assert content.text is not None
        assert "Skill Body" in content.text
        assert content.metadata.get("name") == "test-skill"

    def test_validate_missing_frontmatter(self) -> None:
        asset_type = SkillAssetType()
        content = AssetContent(text="No frontmatter here")
        errors = asset_type.validate(content)
        assert len(errors) > 0


class TestImageAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = ImageAssetType()
        assert asset_type.name == "image"
        assert ".txt" in asset_type.file_extensions

    def test_load_image_prompt(self, tmp_path: Path) -> None:
        path = tmp_path / "image-prompt.txt"
        path.write_text("A sunset over mountains, oil painting style")

        asset_type = ImageAssetType()
        content = asset_type.load(path)
        assert content.text == "A sunset over mountains, oil painting style"

    def test_validate_nonempty(self) -> None:
        asset_type = ImageAssetType()
        errors = asset_type.validate(AssetContent(text="A cat"))
        assert errors == []


class TestAssetRegistry:
    def test_register_and_get(self) -> None:
        registry = AssetRegistry()
        prompt_type = PromptAssetType()
        registry.register_type(prompt_type)
        assert registry.get("prompt") is prompt_type

    def test_get_unknown_returns_none(self) -> None:
        registry = AssetRegistry()
        assert registry.get("unknown") is None

    def test_list_registered(self) -> None:
        registry = AssetRegistry()
        registry.register_type(PromptAssetType())
        registry.register_type(SkillAssetType())
        names = registry.list_types()
        assert "prompt" in names
        assert "skill" in names

    def test_decorator_registration(self) -> None:
        registry = AssetRegistry()

        @registry.register_decorator("custom")
        class CustomType:
            name = "custom"
            file_extensions = [".custom"]
            def load(self, path):
                return AssetContent(text=path.read_text())
            def save(self, content, path):
                path.write_text(content.text or "")
            def validate(self, content):
                return []
            def default_evaluation(self):
                return {"asset_type": "custom", "criteria": []}
            def render_for_prompt(self, content):
                return content.text or ""

        assert registry.get("custom") is not None
