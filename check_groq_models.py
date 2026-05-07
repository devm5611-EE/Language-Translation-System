#!/usr/bin/env python3
"""
Quick script to check which Groq models are currently available and working.
"""
import sys
import os

# Add linguaflow to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linguaflow'))

from groq import Groq
from config import Config

def check_model(client, model_name):
    """Test if a model is working."""
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Say 'OK' if you can read this."}
            ],
            max_tokens=10,
            temperature=0.0
        )
        return True, response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "decommissioned" in error_msg.lower():
            return False, "DECOMMISSIONED"
        elif "not found" in error_msg.lower():
            return False, "NOT FOUND"
        else:
            return False, f"ERROR: {error_msg[:100]}"

def main():
    print("=" * 70)
    print("GROQ MODEL AVAILABILITY CHECK")
    print("=" * 70)
    print()
    
    # Initialize Groq client
    try:
        client = Groq(api_key=Config.GROQ_API_KEY)
        print("✅ Groq API Key: Valid")
        print()
    except Exception as e:
        print(f"❌ Groq API Key: Invalid - {e}")
        return
    
    # Test current configured models
    print("Testing Currently Configured Models:")
    print("-" * 70)
    
    working_models = []
    failed_models = []
    
    for model in Config.SUPPORTED_MODELS:
        print(f"\nTesting: {model}")
        is_working, result = check_model(client, model)
        
        if is_working:
            print(f"  ✅ Status: WORKING")
            print(f"  Response: {result}")
            working_models.append(model)
        else:
            print(f"  ❌ Status: FAILED")
            print(f"  Reason: {result}")
            failed_models.append((model, result))
    
    # Test some alternative models
    print("\n" + "=" * 70)
    print("Testing Alternative Models:")
    print("-" * 70)
    
    alternative_models = [
        "llama-3.3-70b-versatile",
        "llama-3.2-90b-text-preview",
        "llama-3.2-11b-text-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-1b-preview",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
    ]
    
    for model in alternative_models:
        print(f"\nTesting: {model}")
        is_working, result = check_model(client, model)
        
        if is_working:
            print(f"  ✅ Status: WORKING")
            print(f"  Response: {result}")
            if model not in working_models:
                working_models.append(model)
        else:
            print(f"  ❌ Status: FAILED")
            print(f"  Reason: {result}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    print(f"✅ Working Models ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    
    print()
    print(f"❌ Failed Models ({len(failed_models)}):")
    for model, reason in failed_models:
        print(f"   • {model} - {reason}")
    
    print()
    print("=" * 70)
    
    if working_models:
        print("\n✅ RECOMMENDED CONFIGURATION:")
        print()
        print("SUPPORTED_MODELS = [")
        for model in working_models[:5]:  # Limit to 5 models
            print(f'    "{model}",')
        print("]")
        print(f'DEFAULT_MODEL = "{working_models[0]}"')
    else:
        print("\n❌ NO WORKING MODELS FOUND!")
    
    print()

if __name__ == "__main__":
    main()
