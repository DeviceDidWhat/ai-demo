#!/usr/bin/env python3
"""Test the EditParams validation for old_string == new_string"""

from tools.builtin.edit_file import EditParams
from pydantic import ValidationError

def test_identical_strings_raises_error():
    """Test that identical old_string and new_string raises ValidationError"""
    try:
        params = EditParams(
            path="test.py",
            old_string="def foo():",
            new_string="def foo():",  # Same as old_string
            replace_all=False
        )
        print("❌ FAILED: Expected ValidationError but got none")
        return False
    except ValidationError as e:
        error_msg = str(e)
        if "old_string and new_string must be different" in error_msg:
            print("✓ PASSED: Validation correctly rejects identical strings")
            print(f"  Error message: {error_msg.split(chr(10))[0]}")
            return True
        else:
            print(f"❌ FAILED: Got ValidationError but with unexpected message: {e}")
            return False

def test_different_strings_accepted():
    """Test that different old_string and new_string is accepted"""
    try:
        params = EditParams(
            path="test.py",
            old_string="def foo():",
            new_string="def bar():",  # Different
            replace_all=False
        )
        print("✓ PASSED: Different strings are accepted")
        return True
    except ValidationError as e:
        print(f"❌ FAILED: Unexpected ValidationError: {e}")
        return False

def test_empty_old_string_allows_same_new():
    """Test that empty old_string allows any new_string (even if same placeholder)"""
    try:
        params = EditParams(
            path="test.py",
            old_string="",  # Empty for new file
            new_string="",  # Can be empty for new file
            replace_all=False
        )
        print("✓ PASSED: Empty old_string allows any new_string (for new files)")
        return True
    except ValidationError as e:
        print(f"❌ FAILED: Unexpected ValidationError for new file: {e}")
        return False

if __name__ == "__main__":
    print("Testing EditParams validation...\n")
    
    results = [
        test_identical_strings_raises_error(),
        test_different_strings_accepted(),
        test_empty_old_string_allows_same_new(),
    ]
    
    print(f"\nResults: {sum(results)}/{len(results)} tests passed")
    exit(0 if all(results) else 1)
