# Copyright 2026 Google LLC
# Unit tests for image generation tool

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.image_tools import generate_fitness_image


@pytest.mark.asyncio
async def test_generate_fitness_image_success() -> None:
    mock_context = AsyncMock()
    mock_context.save_artifact = AsyncMock(return_value=1)

    fake_image_bytes = b"fake_jpeg_bytes"

    mock_part = MagicMock()
    mock_part.inline_data.data = fake_image_bytes
    mock_part.inline_data.mime_type = "image/jpeg"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_gen_response = MagicMock()
    mock_gen_response.candidates = [mock_candidate]

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_gen_response

    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket

    with (
        patch("app.image_tools.genai.Client", return_value=mock_genai_client),
        patch("app.image_tools.storage.Client", return_value=mock_storage_client),
    ):
        result_json = await generate_fitness_image(
            prompt="A sleek carbon-fiber trail running shoe", tool_context=mock_context
        )
        data = json.loads(result_json)

        assert data["status"] == "success"
        assert "image_url" in data
        assert data["image_url"].startswith("https://storage.googleapis.com/apex-coach-media-qwiklabs-gcp-03-fcbe5502dab4/")
        assert mock_context.save_artifact.called
        assert mock_blob.upload_from_string.called
