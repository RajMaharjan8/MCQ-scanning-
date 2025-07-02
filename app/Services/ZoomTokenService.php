<?php
namespace App\Services;
use App\Models\ZoomAuthorization;
use Illuminate\Support\Facades\Http;

class ZoomTokenService
{
    public function validToken(): string       // no userId param needed
    {
        $auth = ZoomAuthorization::firstWhere('user_id', 1);
        if (!$auth) {
            throw new \RuntimeException('Zoom not yet authorised.');
        }

        if ($auth->isExpired()) {
            $this->refresh($auth);
        }

        return $auth->access_token;
    }

    protected function refresh(ZoomAuthorization $auth): void
    {
        $res = Http::asForm()
            ->withBasicAuth('BHgdEprYQQagzIRJGdvCng', 'pfWBR82Et0Q4pzwuHOKHW3rKuvoUjY5o')
            ->post('https://zoom.us/oauth/token', [
                'grant_type' => 'refresh_token',
                'refresh_token' => $auth->refresh_token,
            ]);

        if (!$res->ok()) {
            throw new \RuntimeException('Zoom token refresh failed', 500);
        }

        $data = $res->json();

        $auth->update([
            'access_token' => $data['access_token'],
            'refresh_token' => $data['refresh_token'],
            'expires_at' => now()->addSeconds($data['expires_in'] ?? 3600),
        ]);
    }
}
