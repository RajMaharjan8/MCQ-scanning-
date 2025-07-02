<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class McqController extends Controller
{
    public function check(Request $request)
    {
        if ($request->hasFile('image_data') && $request->file('image_data')->isValid()) {
            $file = $request->file('image_data');

            $fileName = uniqid() . '_' . preg_replace('/[^a-zA-Z0-9._-]/', '', $file->getClientOriginalName());
            $path = $file->storeAs('uploads', $fileName, 'public');
            $imagePath = storage_path('app/public/' . $path);

            $script = base_path('fivegride_grader.py');
            if (!file_exists($script)) {
                return response()->json(['error' => 'Python script not found'], 500);
            }

            $python = '/home/raj/venv/grader/bin/python';

            $cmd = sprintf(
                '%s %s %s 2>&1',                  // 🠔 add “2>&1” to merge stderr into stdout
                escapeshellcmd($python),
                escapeshellarg($script),
                escapeshellarg($imagePath)
            );

            $response = shell_exec($cmd);
            \Log::error('[grader] ' . $response);    // or dump($response) while testing
            $payload = json_decode($response, true);

            if (is_null($payload)) {
                return response()->json([
                    'error' => 'Failed to process image',
                    'raw_out' => $response,
                ], 500);
            }
            return response()->json([
                'url' => Storage::url($path),
                'result' => $payload
            ], 201);
        }

        return response()->json(['error' => 'No valid file uploaded'], 422);
    }

}
