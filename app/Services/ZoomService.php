<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Cache;

class ZoomService
{
    protected $accountId;
    protected $clientId;
    protected $clientSecret;
    protected $baseUrl;

    public function __construct()
    {
        $this->accountId = 'I4slFdauS5-WaO5uUYQqmA';
        $this->clientId = 'CJDEnADVSYGeuvG0sRwMrQ';
        $this->clientSecret = 'oqv93e81C9fc2d62q56y0lQQn60WC9Cu';
        $this->baseUrl = 'https://api.zoom.us/v2';
    }

    /**
     * Get OAuth access token
     */

    protected function getAccessToken()
    {
        return Cache::remember('zoom_access_token', 3500, function () {
            $response = Http::withBasicAuth($this->clientId, $this->clientSecret)
                ->asForm()
                ->post('https://zoom.us/oauth/token', [
                    'grant_type' => 'account_credentials',
                    'account_id' => $this->accountId,
                ]);

            if ($response->failed()) {
                throw new \Exception('Failed to get Zoom access token: ' . $response->body());
            }

            return $response->json()['access_token'];
        });
    }

    /**
     * Create a Zoom meeting and return the join URL
     */
    public function createMeeting(array $data)
    {
        $token = $this->getAccessToken();
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

        $ch = \curl_init();
        curl_setopt($ch, CURLOPT_URL, "{$this->baseUrl}/users/{$userId}/meetings");
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            "Authorization: Bearer $token",
            "Content-Type: application/json",
        ]);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        if (curl_errno($ch)) {
            throw new \Exception('Curl error: ' . curl_error($ch));
        }

        curl_close($ch);

        if ($httpCode >= 400) {
            throw new \Exception("Zoom API error (HTTP $httpCode): $response");
        }

        $meeting = json_decode($response, true);
        dd($meeting);
        return [
            'meeting_id' => $meeting['id'],
            'join_url' => $meeting['join_url'],
            'admin_url'=> $meeting['start_url'],
            'start_time' => $meeting['start_time'],
            'password'=> $meeting['password'],
            'enc_password'=> $meeting['encrypted_password'],
            'topic' => $meeting['topic'],
            'token'=> $token
        ];
    }

}