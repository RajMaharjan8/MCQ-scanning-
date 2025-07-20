<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Questions extends Model
{
    protected $table = "questions";
    protected $fillable = ['question', 'options', 'order', 'answer'];
    protected $casts = [
        'options' => 'array',
    ];
}
