#!/usr/bin/env python3
"""
tutorial_poc.py - HTTP API Testing Script for Manga Image Translator
This script demonstrates how to test the Manga Image Translator FastAPI endpoints
using HTTP requests.

Endpoints:
- /translate/json - Translate image and return JSON
- /translate/image - Translate image and return PNG
- /translate/batch/json - Batch translate images
- /queue-size - Get queue size

Usage:
    python tutorial_poc.py --host localhost --port 8000 --test all
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests


class MangaTranslatorAPIClient:
    """Client for testing Manga Image Translator API endpoints."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.base_url = f"http://{host}:{port}"
        self.host = host
        self.port = port

    def test_health(self) -> Dict[str, Any]:
        """Test the root endpoint to verify server is running."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.text else {"message": "Server is running"},
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def translate_json(self, image_path: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Translate an image and return JSON results.

        Args:
            image_path: Path to the input image file
            config: Optional translation config dict

        Returns:
            Response from the API containing translated image data
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"File not found: {image_path}"}

        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/png")}
                data = {"config": json.dumps(config or {})}
                response = requests.post(
                    f"{self.base_url}/translate/with-form/json",
                    files=files,
                    data=data,
                    timeout=300,
                )
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def translate_image(self, image_path: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Translate an image and return the result as PNG.

        Args:
            image_path: Path to the input image file
            config: Optional translation config dict

        Returns:
            Response containing the translated image
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"File not found: {image_path}"}

        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/png")}
                data = {"config": json.dumps(config or {})}
                response = requests.post(
                    f"{self.base_url}/translate/with-form/image",
                    files=files,
                    data=data,
                    timeout=300,
                )
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.headers.get("content-type", "unknown"),
                    "image_data": response.content,
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def translate_json_stream(self, image_path: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Translate an image using streaming JSON response.

        Args:
            image_path: Path to the input image file
            config: Optional translation config dict

        Returns:
            Response containing streaming translation progress
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"File not found: {image_path}"}

        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/png")}
                data = {"config": json.dumps(config or {})}
                response = requests.post(
                    f"{self.base_url}/translate/with-form/json/stream",
                    files=files,
                    data=data,
                    timeout=300,
                )
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.headers.get("content-type", "unknown"),
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def queue_size(self) -> Dict[str, Any]:
        """Get the current queue size."""
        try:
            response = requests.get(f"{self.base_url}/queue-size", timeout=5)
            return {
                "success": True,
                "status_code": response.status_code,
                "data": {"queue_size": response.json()},
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def results_list(self) -> Dict[str, Any]:
        """List all result directories."""
        try:
            response = requests.get(f"{self.base_url}/results/list", timeout=5)
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def print_response(self, response: Dict[str, Any], max_text_length: int = 500):
        """Pretty print an API response."""
        if not response.get("success"):
            print(f"[ERROR] {response.get('error', 'Unknown error')}")
            return

        print(f"[INFO] Status: {response.get('status_code', 'N/A')}")
        data = response.get("data", {})

        # Print text/JSON content
        if isinstance(data, dict):
            print(f"\n[DATA]")
            print(json.dumps(data, indent=2)[:max_text_length])
        elif isinstance(data, str):
            print(f"\n[DATA] (length: {len(data)})")
            print("-" * 50)
            print(data[:max_text_length] + "..." if len(data) > max_text_length else data)
            print("-" * 50)

        # Print image info if present
        if "image_data" in response:
            img_data = response["image_data"]
            print(f"\n[IMAGE] Type: {response.get('data', 'N/A')}, Size: {len(img_data)} bytes")


def create_sample_image(output_path: str) -> str:
    """Create a sample image for testing (if it doesn't exist)."""
    try:
        from PIL import Image
    except ImportError:
        print("[INFO] PIL not available, skipping sample image creation")
        return ""

    # Create a simple placeholder image
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    img.save(output_path, "PNG")
    return output_path


def run_tests(client: MangaTranslatorAPIClient, test_type: str = "all") -> Dict[str, bool]:
    """Run API tests based on the specified type.

    Args:
        client: MangaTranslatorAPIClient instance
        test_type: Type of tests to run ("all", "health", "translate", "queue", "results")

    Returns:
        Dictionary of test results
    """
    results = {}

    print("=" * 60)
    print("Manga Image Translator API Test Suite")
    print("=" * 60)
    print(f"Base URL: {client.base_url}")
    print(f"Test Type: {test_type}")
    print("=" * 60)

    # Test 1: Health check (always run)
    print("\n[TEST 1] Health Check")
    result = client.test_health()
    results["health"] = result.get("success", False)
    client.print_response(result)
    time.sleep(1)

    if test_type in ("all", "health"):
        return results

    # Test 2: Queue size
    if test_type in ("all", "queue"):
        print("\n[TEST 2] Queue Size")
        result = client.queue_size()
        results["queue_size"] = result.get("success", False)
        client.print_response(result)
        time.sleep(1)

    # Test 3: Results list
    if test_type in ("all", "results"):
        print("\n[TEST 3] Results List")
        result = client.results_list()
        results["results_list"] = result.get("success", False)
        client.print_response(result)
        time.sleep(1)

    # Test 4: Translation (requires actual image file)
    if test_type in ("all", "translate"):
        print("\n[TEST 4] Image Translation (JSON)")
        print("[INFO] Creating sample image...")
        sample_img = "/tmp/manga_sample.png"
        create_sample_image(sample_img)

        if os.path.exists(sample_img):
            result = client.translate_json(sample_img, config={"source_lang": "ja", "target_lang": "en"})
            results["translate_json"] = result.get("success", False)
            client.print_response(result)
        else:
            print("[INFO] Skipping translation test (no sample image)")
            results["translate_json"] = False

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    print("=" * 60)

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manga Image Translator API Testing Script"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="API host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)",
    )
    parser.add_argument(
        "--test",
        choices=["all", "health", "translate", "queue", "results"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument(
        "--image",
        help="Path to image for translation test",
    )
    parser.add_argument(
        "--output",
        choices=["summary", "json"],
        default="summary",
        help="Output format (default: summary)",
    )

    args = parser.parse_args()

    # Create client
    client = MangaTranslatorAPIClient(host=args.host, port=args.port)

    # If image provided, run translation test
    if args.image:
        result = client.translate_json(args.image)
        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            client.print_response(result)

    else:
        # Run full test suite
        results = run_tests(client, args.test)

        if args.output == "json":
            print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
