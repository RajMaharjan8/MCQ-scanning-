<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Services\ZoomService;
use Illuminate\Http\Request;

class ZoomController extends Controller
{
    protected $zoomService;

    public function __construct(ZoomService $zoomService)
    {
        $this->zoomService = $zoomService;
    }

    public function createMeeting(Request $request)
    {
        try {
            $meeting = $this->zoomService->createMeeting([
                'topic' => $request->input('topic', 'New Meeting'),
                'start_time' => $request->input('start_time'),
                'duration' => $request->input('duration', 60),
                'timezone' => $request->input('timezone', 'UTC'),
                'password' => $request->input('password'),
                'agenda' => $request->input('agenda'),
                'host_video' => $request->input('host_video', true),
                'participant_video' => $request->input('participant_video', true),
                'join_before_host' => $request->input('join_before_host', false),
                'mute_upon_entry' => $request->input('mute_upon_entry', false),
                'waiting_room' => $request->input('waiting_room', false),
                'audio' => $request->input('audio', 'both'),
            ]);

            return response()->json([
                'success' => true,
                'data' => $meeting,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    
}