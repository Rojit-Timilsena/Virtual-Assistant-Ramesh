from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import os
import sys
from . import ramesh_core
from .ramesh_core import processCommand, clean_text  # Import the function from ramesh_core.py

def index(request):
    return render(request, 'assistant/index.html')

def debug_view(request):
    return render(request, 'assistant/debug.html')

@csrf_exempt
def jarvis_api(request):
    if request.method == "GET":
        command = request.GET.get('command', '').lower()
        if command:
            try:
                # Process the command using ramesh_core without speaking
                response_text = processCommand(command, speak_enabled=False)  # Calling processCommand from ramesh_core.py
                return JsonResponse({'response': response_text})
            except Exception as e:
                import traceback
                error_message = f"Error: {str(e)}"
                print(f"API error: {error_message}")
                print(traceback.format_exc())
                return JsonResponse({'error': error_message})
        else:
            return JsonResponse({'error': 'No command received'})

@csrf_exempt
def test_gemini(request):
    """Debug endpoint to test Gemini API directly"""
    try:
        import requests
        import json
        from dotenv import load_dotenv
        import os
        import traceback
        
        # Load environment variables directly
        from pathlib import Path
        dotenv_path = Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=dotenv_path)
        api_key = os.getenv('gemini_api_key')
        
        # Debug info
        debug_info = {
            'api_key_loaded': bool(api_key),
            'api_key_prefix': api_key[:5] + '...' if api_key else None,
            'env_file_path': str(dotenv_path),
            'env_file_exists': os.path.exists(dotenv_path)
        }
        
        if not api_key:
            return JsonResponse({
                'error': 'No API key found', 
                'debug': debug_info
            })
        
        # Test query
        query = request.GET.get('query', 'Hello, please respond with a short test message')
        
        # Direct API call using requests
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts":[{"text": query}]
                }
            ],
            "system_instruction": {
                "parts": [
                    {"text": "You are Ramesh, a helpful personal assistant. Your name is Ramesh. When asked about your identity, always introduce yourself as Ramesh, not as a language model, AI, or any other name like Bard or Gemini. You are created to assist users with various tasks including answering questions, providing information, and performing other helpful actions."}
                ]
            },
            "generation_config": {
                "temperature": 0.7
            }
        }
        
        # Add API key as query parameter
        params = {
            "key": api_key
        }
        
        # Make the API call
        response = requests.post(url, params=params, headers=headers, json=data)
        
        # Add API response details to debug info
        debug_info.update({
            'status_code': response.status_code,
            'response_length': len(response.text),
            'http_headers': dict(response.headers)
        })
        
        if response.status_code == 200:
            result = response.json()
            debug_info['response_structure'] = {k: type(v).__name__ for k, v in result.items()}
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    response_text = ''.join([part.get('text', '') for part in parts])
                    # Clean the response text
                    response_text = clean_text(response_text)
                    
                    return JsonResponse({
                        'success': True, 
                        'response': response_text,
                        'debug': debug_info
                    })
                else:
                    return JsonResponse({
                        'error': 'Response format unexpected',
                        'raw_response': result,
                        'debug': debug_info
                    })
            else:
                return JsonResponse({
                    'error': 'No response candidates found',
                    'raw_response': result,
                    'debug': debug_info
                })
        else:
            return JsonResponse({
                'error': f'API Error: {response.status_code}',
                'response_text': response.text,
                'debug': debug_info
            })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        })
