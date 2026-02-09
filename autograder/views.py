# autograder/views.py
import os
import json
import re
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import user_passes_test
from .models import TeacherQuestion
from .ocr_engine import run_ocr
from .text_correction import safe_correct_word, auto_build_ocr_fixes
from .grader import grade_text
from .config import MODEL_ANSWER


# ==================== HELPER FUNCTIONS ====================

def load_fixes():
    path = os.path.join(os.path.dirname(__file__), 'ocr_fixes.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_fixes(fixes):
    path = os.path.join(os.path.dirname(__file__), 'ocr_fixes.json')
    with open(path, 'w') as f:
        json.dump(fixes, f, indent=2)


# ==================== STUDENT GRADING API ====================

@csrf_exempt
def grade_answer(request):
    """
    Student submits image + question_id → OCR → Grade → Return result
    NO database save for student answers
    """
    if request.method == 'POST' and request.FILES.get('image'):
        # Get question ID from request
        question_id = request.POST.get('question_id', '').strip()
        
        print(f"\n{'='*60}")
        print(f"🔍 GRADING REQUEST RECEIVED")
        print(f"🔍 Received question_id: '{question_id}'")
        print(f"🔍 All available question_ids in DB: {[q.question_id for q in TeacherQuestion.objects.all()]}")
        print(f"{'='*60}\n")
        
        # Load teacher's question and keywords
        teacher_question = None
        expected_keywords = []
        model_answer = ""
        
        if question_id:
            try:
                teacher_question = TeacherQuestion.objects.get(question_id=question_id)
                expected_keywords = teacher_question.get_expected_keywords()
                model_answer = teacher_question.model_answer
                
                print(f"✅ Question found: {teacher_question.question_text[:80]}...")
                print(f"✅ Expected keywords count: {len(expected_keywords)}")
                print(f"✅ Expected keywords: {expected_keywords}")
                print(f"✅ Model answer length: {len(model_answer)} chars")
                
            except TeacherQuestion.DoesNotExist:
                print(f"❌ ERROR: Question with ID '{question_id}' not found in database!")
                print(f"❌ Using fallback to config.py keywords")
                expected_keywords = []
                model_answer = MODEL_ANSWER
        else:
            print(f"⚠️  WARNING: No question_id provided in request!")
            print(f"⚠️  Using fallback to config.py keywords")
            expected_keywords = []
            model_answer = MODEL_ANSWER
        
        # If no keywords from database, use config fallback
        if not expected_keywords:
            from .config import EXPECTED_KEYWORDS
            expected_keywords = list(EXPECTED_KEYWORDS)
            print(f"⚠️  Using config.py EXPECTED_KEYWORDS as fallback")
            print(f"⚠️  Fallback keywords count: {len(expected_keywords)}")
        
        image = request.FILES['image']
        filename = f"temp_{image.name}"
        saved_path = default_storage.save(filename, image)
        full_path = default_storage.path(saved_path)

        try:
            # 1. Run OCR
            print(f"\n{'='*60}")
            print(f"📷 RUNNING OCR...")
            print(f"{'='*60}")
            raw_results = run_ocr(full_path)
            print(f"✅ Raw OCR lines: {len(raw_results)}")
            for i, line in enumerate(raw_results[:5], 1):  # First 5 lines
                print(f"   Line {i}: {line[:100]}...")
            if len(raw_results) > 5:
                print(f"   ... and {len(raw_results) - 5} more lines")

            # 2. Load fixes
            ocr_fixes = load_fixes()
            print(f"\n🔧 Loaded {len(ocr_fixes)} OCR fixes from file")

            # 3. Tokenize & correct
            print(f"\n{'='*60}")
            print(f"🔤 TOKENIZING AND CORRECTING TEXT...")
            print(f"{'='*60}")
            all_tokens = []
            corrected_lines = []
            for line in raw_results:
                tokens = re.split(r'[_\s~@#$%^&*+=]+', line)
                corrected_tokens = []
                for token in tokens:
                    if not token or not any(c.isalpha() for c in token):
                        continue
                    all_tokens.append(token)
                    corrected = safe_correct_word(token, ocr_fixes)
                    if corrected:
                        corrected_tokens.append(corrected)
                if corrected_tokens:
                    corrected_lines.append(" ".join(corrected_tokens))

            final_text = " ".join(corrected_lines).strip()
            print(f"✅ Total tokens extracted: {len(all_tokens)}")
            print(f"✅ Final corrected text length: {len(final_text)} chars")
            print(f"✅ Corrected text preview: {final_text[:200]}...")

            # 4. Auto-generate new fixes
            print(f"\n{'='*60}")
            print(f"🤖 AUTO-BUILDING NEW OCR FIXES...")
            print(f"{'='*60}")
            model_words = set(model_answer.lower().split())
            new_fixes = auto_build_ocr_fixes(all_tokens, model_words)
            
            if new_fixes:
                print(f"✅ Found {len(new_fixes)} new OCR fixes:")
                for old, new in list(new_fixes.items())[:10]:  # First 10
                    print(f"   '{old}' → '{new}'")
                ocr_fixes.update(new_fixes)
                save_fixes(ocr_fixes)
                print(f"✅ Saved {len(ocr_fixes)} total fixes to file")
            else:
                print(f"ℹ️  No new OCR fixes found")

            # 5. Grade using teacher's expected keywords
            print(f"\n{'='*60}")
            print(f"📊 GRADING STUDENT ANSWER...")
            print(f"{'='*60}")
            print(f"📝 Expected keywords for grading: {expected_keywords}")
            
            score, matched, missing = grade_text(final_text, expected_keywords)
            
            print(f"✅ Matched keywords: {len(matched)}")
            if matched:
                print(f"   Matched: {list(matched)[:20]}")  # First 20
                if len(matched) > 20:
                    print(f"   ... and {len(matched) - 20} more")
            else:
                print(f"   ❌ No keywords matched!")
            
            print(f"❌ Missing keywords: {len(missing)}")
            if missing:
                print(f"   Missing: {list(missing)[:20]}")  # First 20
                if len(missing) > 20:
                    print(f"   ... and {len(missing) - 20} more")
            
            print(f"📈 Score: {score:.2%} ({len(matched)}/{len(expected_keywords)} keywords matched)")

            # 6. Return result (NO database save)
            response_data = {
                "success": True,
                "grade": round(score * 100, 2),  # Return as percentage
                "corrected_text": final_text,
                "matched": sorted(list(matched)),
                "missing": sorted(list(missing)),
                "question_id": question_id,
                "total_keywords": len(expected_keywords),
                "matched_count": len(matched),
                "debug": {
                    "question_found": teacher_question is not None,
                    "keywords_source": "database" if teacher_question and teacher_question.expected_keywords else "config.py",
                    "expected_keywords": expected_keywords,
                    "raw_ocr_lines": len(raw_results),
                    "total_tokens": len(all_tokens)
                }
            }
            
            print(f"\n{'='*60}")
            print(f"✅ GRADING COMPLETE!")
            print(f"✅ Final Grade: {response_data['grade']}%")
            print(f"{'='*60}\n")
            
            return JsonResponse(response_data)

        except Exception as e:
            import traceback
            print(f"\n{'='*60}")
            print(f"❌ ERROR OCCURRED:")
            print(f"{'='*60}")
            print(traceback.format_exc())
            print(f"{'='*60}\n")
            
            return JsonResponse({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=500)
        finally:
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"🧹 Cleaned up temp file: {full_path}")
                except:
                    pass

    return JsonResponse({"error": "POST request with image file required"}, status=400)


# ==================== TEACHER INTERFACES ====================

@user_passes_test(lambda u: u.is_staff)
def teacher_dashboard(request):
    """Display all teacher questions"""
    questions = TeacherQuestion.objects.all().order_by('-created_at')
    return render(request, 'teacher/dashboard.html', {
        'questions': questions
    })


@user_passes_test(lambda u: u.is_staff)
def add_teacher_question(request):
    """Add or edit a teacher question"""
    success_message = None
    error_message = None
    
    if request.method == 'POST':
        question_id = request.POST.get('question_id', '').strip()
        question_text = request.POST.get('question_text', '').strip()
        expected_keywords = request.POST.get('expected_keywords', '').strip()
        model_answer = request.POST.get('model_answer', '').strip()
        
        if not question_id:
            error_message = "Question ID is required!"
        elif not question_text:
            error_message = "Question text is required!"
        elif not expected_keywords:
            error_message = "Expected keywords are required!"
        elif not model_answer:
            error_message = "Model answer is required!"
        else:
            try:
                # Create or update question
                question, created = TeacherQuestion.objects.update_or_create(
                    question_id=question_id,
                    defaults={
                        'question_text': question_text,
                        'expected_keywords': expected_keywords,
                        'model_answer': model_answer
                    }
                )
                
                # Parse and show keywords for confirmation
                parsed_keywords = question.get_expected_keywords()
                
                success_message = f"✅ Question '{question_id}' {'created' if created else 'updated'} successfully!"
                success_message += f"\n📝 Parsed {len(parsed_keywords)} keywords: {', '.join(parsed_keywords[:10])}"
                if len(parsed_keywords) > 10:
                    success_message += f" ... (+{len(parsed_keywords) - 10} more)"
                
                print(f"\n{'='*60}")
                print(f"✅ TEACHER QUESTION SAVED")
                print(f"{'='*60}")
                print(f"ID: {question_id}")
                print(f"Keywords: {parsed_keywords}")
                print(f"{'='*60}\n")
                
            except Exception as e:
                error_message = f"Error saving question: {str(e)}"
    
    # GET request or after POST - show form
    questions = TeacherQuestion.objects.all()
    return render(request, 'teacher/add_question.html', {
        'questions': questions,
        'success_message': success_message,
        'error_message': error_message
    })


@user_passes_test(lambda u: u.is_staff)
def delete_teacher_question(request, question_id):
    """Delete a teacher question"""
    try:
        question = TeacherQuestion.objects.get(question_id=question_id)
        question.delete()
        print(f"✅ Deleted question: {question_id}")
    except TeacherQuestion.DoesNotExist:
        print(f"⚠️  Question not found: {question_id}")
        pass
    
    return redirect('teacher_dashboard')


# ==================== STUDENT INTERFACE ====================

def student_interface(request):
    """Student upload page"""
    questions = TeacherQuestion.objects.all()
    
    # Debug: Show available questions
    print(f"\n{'='*60}")
    print(f"📚 STUDENT INTERFACE - Available Questions:")
    print(f"{'='*60}")
    for q in questions:
        kw_count = len(q.get_expected_keywords())
        print(f"ID: '{q.question_id}' | Keywords: {kw_count} | Question: {q.question_text[:60]}...")
    print(f"{'='*60}\n")
    
    return render(request, 'student/upload.html', {
        'questions': questions
    })