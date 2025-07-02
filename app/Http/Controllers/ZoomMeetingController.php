<?php
// app/Http/Controllers/ZoomController.php

namespace App\Http\Controllers;

use App\Models\ZoomAuthorization;
use App\Services\ZoomTokenService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Session;


class ZoomMeetingController extends Controller
{
    private $clientId = 'BHgdEprYQQagzIRJGdvCng';
    private $clientSecret = 'pfWBR82Et0Q4pzwuHOKHW3rKuvoUjY5o';
    private $redirectUri = 'http://127.0.0.1:8000/api/zoom/callback';
    protected $zoom_auth;
    public function __construct(ZoomAuthorization $zoom_auth)
    {
        $this->zoom_auth = $zoom_auth;
    }

    public function redirectToZoom()
    {
        $authorizationUrl = 'https://zoom.us/oauth/authorize?' . http_build_query([
            'response_type' => 'code',
            'client_id' => $this->clientId,
            'redirect_uri' => $this->redirectUri,
        ]);

        return redirect($authorizationUrl);
    }

    public function handleZoomCallback(Request $request)
    {
        $code = $request->query('code');

        $response = Http::asForm()->withBasicAuth($this->clientId, $this->clientSecret)->post('https://zoom.us/oauth/token', [
            'grant_type' => 'authorization_code',
            'code' => $code,
            'redirect_uri' => $this->redirectUri,
        ]);

        if (!$response->ok()) {
            return response()->json(['error' => 'Unable to get access token', 'details' => $response->json()], 500);
        }

        $data = $response->json();
        $expiry = now()->addSeconds($data['expires_in'] ?? 3600);

        $this->zoom_auth->updateOrCreate(
            ['user_id' => 1],
            [
                'access_token' => $data['access_token'],
                'refresh_token' => $data['refresh_token'],
                'expires_at' => $expiry,
            ]
        );


        // Save token in session or database (for now: session)


        return response()->json([
            'message' => 'Zoom authorization successful.',
            'access_token' => $data['access_token'],
            'note' => 'You can now call POST /api/zoom/create-meeting with meeting data.',
            'complete_data' => $data
        ]);
    }

    public function createMeeting(Request $request, ZoomTokenService $zoomToken)
    {
        $data = $request->validate([
            'topic' => 'required|string',
            'start_time' => 'required|date',
            'duration' => 'required|integer',
            'timezone' => 'required|string',
        ]);
        $accessToken = $zoomToken->validToken();

        $zoom = Http::withToken($accessToken)->post(
            'https://api.zoom.us/v2/users/me/meetings',
            [
                'topic' => $data['topic'],
                'type' => 2,
                'start_time' => $data['start_time'],
                'duration' => $data['duration'],
                'timezone' => $data['timezone'],
                'settings' => [
                    'join_before_host' => true,
                    'host_video' => true,
                    'participant_video' => true,
                ],
            ]
        );

        return $zoom->ok()
            ? $zoom->json()
            : response()->json(['error' => 'Zoom API error', 'details' => $zoom->json()], 500);
    }

}