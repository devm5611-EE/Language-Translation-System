#!/usr/bin/env python3
"""
Test script to verify all Groq models work with LinguaFlow translation service.
Updated for Groq model changes (May 2026).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linguaflow'))

from services.translation_service import translate, LANGUAGE_NAMES
from config import Config

def test_all_models():
    """Test translation with all supported models."""
    
    test_text = "Hello, how are you today?"
    target_lang = "es"  # Spanish
    user_id = "test_user_123"
    
    print("=" * 70)
    print("LinguaFlow Translation Service - Model Testing")
    print("=" * 70)
    print(f"\nTest Text: '{test_text}'")
    print(f"Target Language: {LANGUAGE_NAMES.get(target_lang, target_lang)}")
    print(f"User ID: {user_id}\n")
    
    results = []
    
    for model in Config.SUPPORTED_MODELS:
        print(f"\n{'─' * 70}")
        print(f"Testing Model: {model}")
        print(f"{'─' * 70}")
        
        try:
            result = translate(
                source_text=test_text,
                target_lang=target_lang,
                user_id=user_id,
                model=model,
                source_lang="auto"
            )
            
            print(f"✅ Status: SUCCESS")
            print(f"   Translation: {result['translation']}")
            print(f"   Source Lang: {result['source_lang']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Response Time: {result['response_time_ms']}ms")
            print(f"   Cache Hit: {result['cache_hit']}")
            
            results.append({
                'model': model,
                'status': 'SUCCESS',
                'translation': result['translation'],
                'confidence': result['confidence'],
                'response_time': result['response_time_ms']
            })
            
        except Exception as e:
            print(f"❌ Status: FAILED")
            print(f"   Error: {str(e)}")
            
            results.append({
                'model': model,
                'status': 'FAILED',
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}\n")
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    
    print(f"Total Models Tested: {len(results)}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {failed} ❌")
    
    print("\nDetailed Results:")
    print(f"{'Model':<35} {'Status':<10} {'Response Time':<15}")
    print("─" * 60)
    
    for result in results:
        status = result['status']
        model = result['model']
        response_time = f"{result.get('response_time', 'N/A')}ms" if status == 'SUCCESS' else 'N/A'
        print(f"{model:<35} {status:<10} {response_time:<15}")
    
    print(f"\n{'=' * 70}\n")
    
    return successful == len(results)

if __name__ == "__main__":
    try:
        success = test_all_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
