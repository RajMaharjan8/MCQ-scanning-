<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Session;

class ZoomNew
{
    protected $clientId;
    protected $clientSecret;
    protected $redirectUri;
    protected $baseUrl;

    public function __construct()
    {
        $this->clientId = 'BHgdEprYQQagzIRJGdvCng';  // Set in config/services.php
        $this->clientSecret = 'pfWBR82Et0Q4pzwuHOKHW3rKuvoUjY5o';
        $this->redirectUri = 'http://localhost:8000/zoom/callback';
        $this->baseUrl = 'https://api.zoom.us/v2';
    }

    /**
     * Get Zoom OAuth authorization URL to redirect user for consent
     */
    public function getAuthorizationUrl()
    {
        $query = http_build_query([
            'response_type' => 'code',
            'client_id' => $this->clientId,
            'redirect_uri' => $this->redirectUri,
            'scope' => 'user:read user:write meeting:write meeting:read', // scopes needed for meeting creation
            'state' => csrf_token(), // optional CSRF protection
        ]);

        return "https://zoom.us/oauth/authorize?$query";
    }

    /**
     * Exchange authorization code for access token & refresh token
     */
    public function getAccessTokenFromCode(string $code)
    {
        $response = Http::withBasicAuth($this->clientId, $this->clientSecret)
            ->asForm()
            ->post('https://zoom.us/oauth/token', [
                'grant_type' => 'authorization_code',
                'code' => $code,
                'redirect_uri' => $this->redirectUri,
            ]);

        if ($response->failed()) {
            throw new \Exception('Failed to get Zoom access token: ' . $response->body());
        }

        $tokens = $response->json();

        // Store tokens in session or database for later use
        Session::put('zoom_access_token', $tokens['access_token']);
        Session::put('zoom_refresh_token', $tokens['refresh_token']);
        Session::put('zoom_token_expires_in', now()->addSeconds($tokens['expires_in']));

        return $tokens['access_token'];
    }

    /**
     * Refresh access token using refresh token
     */
    public function refreshAccessToken()
    {
        $refreshToken = Session::get('zoom_refresh_token');
        if (!$refreshToken) {
            throw new \Exception('No refresh token found');
        }

        $response = Http::withBasicAuth($this->clientId, $this->clientSecret)
            ->asForm()
            ->post('https://zoom.us/oauth/token', [
                'grant_type' => 'refresh_token',
                'refresh_token' => $refreshToken,
            ]);

        if ($response->failed()) {
            throw new \Exception('Failed to refresh Zoom access token: ' . $response->body());
        }

        $tokens = $response->json();

        // Update tokens in session or database
        Session::put('zoom_access_token', $tokens['access_token']);
        Session::put('zoom_refresh_token', $tokens['refresh_token']);
        Session::put('zoom_token_expires_in', now()->addSeconds($tokens['expires_in']));

        return $tokens['access_token'];
    }

    /**
     * Get a valid access token, refresh if expired
     */
    protected function getValidAccessToken()
    {
        $expiresAt = Session::get('zoom_token_expires_in');
        if (!$expiresAt || now()->greaterThanOrEqualTo($expiresAt)) {
            return $this->refreshAccessToken();
        }

        return Session::get('zoom_access_token');
    }

    /**
     * Create a Zoom meeting
     */
    public function createMeeting(array $data)
    {
        $token = $this->getValidAccessToken();

        // You must specify the userId (usually the authorized user)
        // You can use 'me' or the email of the user
        $userId = 'me';

        $payload = [
            'topic' => $data['topic'] ?? 'New Meeting',
            'type' => 2,
            'start_time' => $data['start_time'] ?? now()->addHour()->toIso8601String(),
            'duration' => $data['duration'] ?? 60,
            'timezone' => $data['timezone'] ?? 'UTC',
            'password' => $data['password'] ?? null,
            'agenda' => $data['agenda'] ?? null,
            'settings' => [
                'host_video' => $data['host_video'] ?? true,
                'participant_video' => $data['participant_video'] ?? true,
                'join_before_host' => $data['join_before_host'] ?? false,
                'mute_upon_entry' => $data['mute_upon_entry'] ?? false,
                'waiting_room' => $data['waiting_room'] ?? false,
                'audio' => $data['audio'] ?? 'both',
            ],
        ];

        $response = Http::withToken($token)
            ->post("{$this->baseUrl}/users/{$userId}/meetings", $payload);

        if ($response->failed()) {
            throw new \Exception('Failed to create Zoom meeting: ' . $response->body());
        }

        return $response->json();
    }
}
