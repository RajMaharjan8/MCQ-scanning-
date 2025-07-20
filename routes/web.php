<?php

use App\Http\Controllers\DocController;
use App\Http\Controllers\ZoomController;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Home/Home');
});

Route::post('/post', [DocController::class, 'getData'])->name('file.post');
Route::get('/questions', [DocController::class, 'getQuestions'])->name('get.post');
Route::post('/reorder', [DocController::class, 'reorder'])->name('reorder.post');
Route::post('/save', [DocController::class, 'saveAnswer'])->name('save.post');


Route::get('start', [ZoomController::class, 'index']);
Route::any('zoom-meeting-create', [ZoomController::class, 'index']);