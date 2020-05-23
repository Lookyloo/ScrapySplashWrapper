function main(splash, args)
    -- Default values
    splash.js_enabled = true
    splash.private_mode_enabled = true
    splash.images_enabled = true
    splash.webgl_enabled = true
    splash.media_source_enabled = true

    -- Force enable things
    splash.plugins_enabled = true
    splash.request_body_enabled = true
    splash.response_body_enabled = true

    -- Would be nice
    splash.indexeddb_enabled = true
    splash.html5_media_enabled = true
    splash.http2_enabled = true

    -- User defined
    splash.resource_timeout = args.resource_timeout
    splash.timeout = args.timeout
    splash:set_user_agent(args.useragent)

   -- Allow to pass cookies
    splash:init_cookies(args.cookies)

    -- Run
    if args.referer then
      ok, reason = splash:go{args.url, headers={
        ['Referer'] = args.referer,
      }}
    else
      ok, reason = splash:go{args.url}
    end

    -- The error options are listed here: https://splash.readthedocs.io/en/stable/scripting-ref.html#splash-go
    -- HTTP errors are fine, we keep going.
    if not ok and not reason:find("http") then
        return {error = reason}
    end
    splash:wait{args.wait}

    -- Page instrumentation
    splash.scroll_position = {y=1000}

    splash:wait{args.wait}

    -- Response
    return {
        har = splash:har(),
        html = splash:html(),
        png = splash:png{render_all=true},
        cookies = splash:get_cookies(),
		last_redirected_url = splash:url()
    }
end
