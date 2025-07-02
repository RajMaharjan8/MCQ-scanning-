<?php

use App\Http\Controllers\McqController;
use App\Http\Controllers\ZoomController;
use App\Http\Controllers\ZoomMeetingController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');


//Direct server to server
Route::post('/zoom/meeting', [ZoomController::class, 'createMeeting']);
// routes/api.php

// Route::get('/zoom/authorize', [ZoomMeetingController::class, 'redirectToZoom']);
// Route::get('/zoom/callback', [ZoomMeetingController::class, 'handleZoomCallback']);
// Route::post('/zoom/create-meeting', [ZoomMeetingController::class, 'createMeeting']);



//Using general App
Route::prefix('zoom')
    ->middleware([
        'api',
        \Illuminate\Cookie\Middleware\EncryptCookies::class,
        \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
        \Illuminate\Session\Middleware\StartSession::class,
    ])
    ->group(function () {
        Route::get('/authorize', [ZoomMeetingController::class, 'redirectToZoom']);
        Route::get('/callback', [ZoomMeetingController::class, 'handleZoomCallback']);
        Route::post('/create-meeting', [ZoomMeetingController::class, 'createMeeting']);
    });



//MCQs
Route::post('/mcq_checking',[McqController::class, 'check']);