<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ZoomAuthorization extends Model
{
    protected $fillable = [
        'user_id',
        'access_token',
        'refresh_token',
        'expires_at',
    ];

    protected $casts = [
        'expires_at' => 'datetime',
    ];

    public function isExpired(): bool
    {
        return now()->gte($this->expires_at->subMinutes(1));
    }
}
