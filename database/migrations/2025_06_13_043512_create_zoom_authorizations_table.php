<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('zoom_authorizations', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('user_id')->default(1);   // keep it if you’ll need it later
            $table->longText('access_token');
            $table->longText('refresh_token');
            $table->timestamp('expires_at');
            $table->timestamps();
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('zoom-authorizations');
    }
};
