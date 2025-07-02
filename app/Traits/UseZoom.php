<?php

namespace App\Traits;

use GuzzleHttp\Client;
use Log;
use Illuminate\Support\Facades\Http;
use App\Models\User;
/**
 * Class SyncsWithFirebase
 * @package App\Traits
 */
trait UseZoom
{
    public $client;
    public $jwt;
    public $headers;

    public function __construct()
    {


        $this->client = new Client();
        $this->accessToken = '9EAv4Xi3QxiKDINdfZNwog';

        $this->headers = [
            'Authorization' => 'Bearer ' . $this->accessToken,
            'Content-Type'  => 'application/json',
            'Accept'        => 'application/json',
        ];
    }

    /**
     * Display a generateZoomToken.
     *
     * @return \Illuminate\Http\Response
     */
    /*public function generateZoomToken()
    {
        return JWT::generateToken(
            [
                'iss' => config('zoom.api_key'),
                'exp' => time() + config('zoom.token_life')
            ],
            config('zoom.api_secret')
        );
    }*/



    function generateZoomAccessToken()
    {
        $apiKey = env('Client_ID');
        $apiSecret = env('Client_Secret');
        $account_id = env('Account_ID');

        $base64Credentials = base64_encode("$apiKey:$apiSecret");

        $url = 'https://zoom.us/oauth/token?grant_type=account_credentials&account_id=' . $account_id;

        $response = Http::withHeaders([
            'Authorization' => "Basic $base64Credentials",
            'Content-Type' => 'application/x-www-form-urlencoded',
        ])->post($url);

        $responseData = $response->json();

        if (isset($responseData['access_token'])) {
            return $responseData['access_token'];
        } else {
            // Log or print the entire response for debugging purposes.
            \Log::error('Zoom OAuth Token Response: ' . json_encode($responseData));

            // Handle the error as needed.
            return null; // You might want to return null or throw an exception here.
        }
    }
    /**
     * Display a zoomRequest.
     *
     * @return \Illuminate\Http\Response
     */
    /*public function zoomRequest()
    {
        $token = $this->generateZoomToken();

        return \Illuminate\Support\Facades\Http::withHeaders([
            //'authorization' => 'Bearer ' . $token,
            //'content-type' => 'application/json',
        ]);
    }*/

    private function retrieveZoomUrl()
    {
        return env('ZOOM_API_URL', '');
    }

    public function toZoomTimeFormat(string $dateTime)
    {
        try {
            $date = new \DateTime($dateTime);

            return $date->format('Y-m-d\TH:i:s');
        } catch (\Exception $e) {
            Log::error('ZoomJWT->toZoomTimeFormat : ' . $e->getMessage());

            return '';
        }
    }

    public function create($data)
    {
        
        $accessToken = $this->generateZoomAccessToken();
        
        $doctor_zoom_id = 'rajmaharjan.makura@gmail.com';
        
        
        $url = 'https://api.zoom.us/v2/users/'.$doctor_zoom_id.'/meetings';

        $response = Http::withToken($accessToken)->post($url, [
            'topic'      => 'Online Meeting',
            'type'       => self::MEETING_TYPE_SCHEDULE,
            'start_time' => time() + config('zoom.token_life'),
            'duration'   => 1,
            'agenda'     => 'Meeting for Patient',
            'timezone' => 'Africa/Cairo',
        ]);
            return [
                'success' => $response->getStatusCode() === 201,
                'data'    => json_decode($response->getBody(), true),
            ];


        if ($response->successful()) {
            return [
                'success' => $response->getStatusCode() === 201,
                'data'    => json_decode($response->getBody(), true),
            ];
        } else {
            return [
                'success' => $response->getStatusCode() === 201,
                'data'    => json_decode($response->getBody(), true),
            ];
            return response()->json(['error' => 'Failed to create a Zoom meeting'], 500);
        }
    }


    public function updatezoom($id, $data)
    {
        $accessToken = $this->generateZoomAccessToken();
        $url = 'https://api.zoom.us/v2/meetings/' . $id;

        $response = Http::withToken($accessToken)->patch($url, [
            'topic' => 'Online Meeting',
            'type' => self::MEETING_TYPE_SCHEDULE,
            'start_time' => $this->toZoomTimeFormat($data['start_time']),
            'duration' => $data['duration'],
            'agenda' => (!empty($data['agenda'])) ? $data['agenda'] : null,
            'timezone' => 'Africa/Cairo',
        ]);

        if ($response->successful()) {
            // Meeting updated successfully
            return [
                'success' => true,
                'data' => $response->json(),
            ];
        } else {
            // Handle the error
            return response()->json(['error' => 'Failed to update the Zoom meeting'], 500);
        }
    }


    public function get($id)
    {
        $path = 'meetings/' . $id;
        $url = $this->retrieveZoomUrl();
        $this->jwt = $this->generateZoomToken();
        $body = [
            'headers' => $this->headers,
            'body'    => json_encode([]),
        ];

        $response =  $this->client->get($url . $path, $body);

        return [
            'success' => $response->getStatusCode() === 204,
            'data'    => json_decode($response->getBody(), true),
        ];
    }

    /**
     * @param string $id
     *
     * @return bool[]
     */

    public function delete($id)
    {
        $accessToken = $this->generateZoomAccessToken();
        $url = 'https://api.zoom.us/v2/meetings/' . $id;

        $response = Http::withToken($accessToken)->delete($url);

        if ($response->successful()) {
            // Meeting deleted successfully
            return [
                'success' => true,
                'data' => $response->json(),
            ];
        } else {
            // Handle the error
            return response()->json(['error' => 'Failed to delete the Zoom meeting'], 500);
        }
    }

/////////////////////////////////////////////////////



  public function zoomRequest()
    {
        $token = $this->generateZoomAccessToken();

        return \Illuminate\Support\Facades\Http::withHeaders([
            'authorization' => 'Bearer ' . $token,
            'content-type' => 'application/json',
        ]);
    }


    public function linkZoom($id, $email)
    {


        $user = User::findOrFail($id);

        if ($user->zoom_id == "") {

            $body = [
                'action' => "create",
                'user_info' => [
                    'email' => $email,
                    'first_name' => $user->name,
                    'type' => 1
                ]
            ];


            $res = $this->zoomPost('users', $body);
             
            $res = json_decode($res->body(), true);
            
            if(isset($res['id']))
            {
                    $user->zoom_id = $res['id'];
            $user->zoom_email = $email;
            $user->save();

            return $data = [
                'message' => 'You have been associated with Ipersona Zoom portol.However, check your email inbox to accept invitation.'
            ];
            }
            
            return $data = ['message' => 'This email is already exist plz use another'];
        

        }

        return $data = [
            'message' => 'You have already linked with Zoom.'
        ];



    }

   public function zoomGet(string $path, array $body = [])
    {
        $request = $this->zoomRequest();
        return $request->get(config('zoom.base_url') . $path, $body);
    }

    /**
     * Display a zoomPost.
     *
     * @return \Illuminate\Http\Response
     */
    public function zoomPost(string $path, array $body = [])
    {
        $request = $this->zoomRequest();
        return $request->post(config('zoom.base_url') . $path, $body);
    }
    
    
    
    
    
    




}