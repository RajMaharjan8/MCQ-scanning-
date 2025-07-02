<?php

use App\Http\Controllers\ZoomController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome')->with('respond', 'MEETING API RESPOND WILL COME IN THIS SECTION');
});
Route::get('start', [ZoomController::class, 'index']);
Route::any('zoom-meeting-create', [ZoomController::class, 'index']);