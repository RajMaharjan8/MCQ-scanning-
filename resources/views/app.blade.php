<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {{-- <title>Document</title> --}}
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @routes
    @inertiaHead
</head>

<body>
    {{-- <a href="{{ url('start') }}">Make A Zoom Meeting Using Oauth2 And Laravel</a>
<br/>
<br/>
<br/>
{{ $respond }} --}}
    @inertia

</body>

</html>
