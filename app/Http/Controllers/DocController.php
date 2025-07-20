<?php

namespace App\Http\Controllers;

use App\Models\Questions;
use Illuminate\Http\Request;
use PhpOffice\PhpWord\IOFactory;

class DocController extends Controller
{
    public function getQuestions()
    {
        $questions = Questions::orderBy('order')->get();
        foreach ($questions as $q) {
            $q->options = json_decode($q->options, true) ?? [];
        }
        return response()->json($questions);
    }


    public function reorder(Request $request)
    {
        $validated = $request->validate([
            'questions' => 'required|array',
            'questions.*.id' => 'required|integer|exists:questions,id',
            'questions.*.order' => 'required|integer',
        ]);
        foreach ($validated['questions'] as $q) {
            Questions::where('id', $q['id'])->update(['order' => $q['order']]);
        }
        return response()->json(['message' => 'Order updated successfully']);
    }

    public function saveAnswer(Request $request)
    {
        $data = $request->validate([
            'answers' => 'required|array',
            'answers.*.question_id' => 'required|integer|exists:questions,id',
            'answers.*.answer' => 'nullable|string',
        ]);
        foreach ($data['answers'] as $q) {
            Questions::where('id', $q['question_id'])->update(['answer' => $q['answer']]);
        }
        return response()->json(['message' => 'Answer updated successfully']);
    }

    public function getData(Request $request)
    {
        $file = $request->file('file');
        if (!$file) {
            return response()->json(['error' => 'No file uploaded'], 400);
        }
        if ($file->getClientOriginalExtension() !== 'docx') {
            return response()->json(['error' => 'Only .docx files are supported'], 400);
        }
        if ($file->getClientMimeType() !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
            return response()->json(['error' => 'Invalid DOCX file'], 400);
        }

        // Ensure directory exists
        $dir = storage_path('app/private/docs');
        if (!file_exists($dir)) {
            mkdir($dir, 0775, true);
        }

        $originalName = $file->getClientOriginalName();
        $sanitized = preg_replace('/\s+/', '_', $originalName);

        // Store in private/docs
        $path = $file->storeAs('private/docs', $sanitized);
        $fullPath = storage_path('app/' . $path);
        \Log::info('File stored at: ' . $fullPath);

        if (!file_exists($fullPath)) {
            \Log::error("File not found after upload at: $fullPath");
            return response()->json(['error' => 'File not found at: ' . $fullPath], 500);
        }

        try {
            $phpWord = \PhpOffice\PhpWord\IOFactory::load($fullPath, 'Word2007');
        } catch (\Exception $e) {
            \Log::error("PhpWord error: " . $e->getMessage());
            return response()->json(['error' => 'PhpWord error: ' . $e->getMessage()], 500);
        }

        // Extract all text from the Word file
        $text = '';
        foreach ($phpWord->getSections() as $section) {
            foreach ($section->getElements() as $element) {
                if (method_exists($element, 'getText')) {
                    $text .= $element->getText() . "\n";
                }
            }
        }

        // Parse questions and options
        $qaPairs = $this->parseQuestionsAndAnswers($text);
        $maxOrder = \App\Models\Questions::max('order') ?? 0;

        // Store each question/options pair in the database
        foreach ($qaPairs as $index => $qa) {
            \App\Models\Questions::create([
                'question' => $qa['question'],
                'options' => json_encode($qa['options'], JSON_UNESCAPED_UNICODE),
                'order' => $maxOrder + $index + 1,
            ]);
        }

        return response()->json(['questions' => $qaPairs]);
    }

    private function parseQuestionsAndAnswers($text)
    {
        // Split and clean lines
        $lines = array_values(array_filter(array_map('trim', explode("\n", $text))));
        $qaPairs = [];
        $startCollecting = false;
        $total = count($lines);
        $i = 0;

        while ($i < $total) {
            $line = $lines[$i];

            // Start after marker if needed
            if (!$startCollecting) {
                if ($line === 'pQL0ff{° M %)') {
                    $startCollecting = true;
                }
                $i++;
                continue;
            }

            // Stop at footer marker
            if ($line === ';dfKt' || strpos($line, 'wGojfb') !== false || strpos($line, ';Dk"0f{') !== false) {
                break;
            }

            if (preg_match('/^\d+\..*$/u', $line)) {
                $question = preg_replace('/^\d+\.\s*/u', '', $line);
                $options = [];
                $j = $i + 1;
                while ($j < $total && count($options) < 4) {
                    $opt = trim($lines[$j]);
                    if ($opt === '') {
                        $j++;
                        continue;
                    }
                    if (preg_match('/^\d+\..*$/u', $opt)) {
                        break;
                    }
                    $options[] = $opt;
                    $j++;
                }
                if (count($options) === 4) {
                    $qaPairs[] = [
                        'question' => $question,
                        'options' => $options,
                    ];
                }
                $i = $j; 
            } else {
                $i++;
            }
        }
        return $qaPairs;
    }





}
