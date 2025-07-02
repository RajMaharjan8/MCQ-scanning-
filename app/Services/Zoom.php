<?php

namespace App\Services\Zoom;

class Zoom
{
    public function createMeeting($data)
    {
        // Example: Logic to interact with Zoom API
        return "Meeting created with data: " . json_encode($data);
    }

    public function getUser($userId)
    {
        // Example: Logic to fetch a Zoom user
        return "Fetched user: " . $userId;
    }
}