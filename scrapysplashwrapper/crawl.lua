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

    -- Set a reasonable viewport
    splash:set_viewport_size(1280, 800)

    -- Run
    if args.referer then
      ok, reason = splash:go{args.url, headers={
        ['Referer'] = args.referer,
      }}
    else
      ok, reason = splash:go{args.url}
    end

    -- The error options are listed here: https://splash.readthedocs.io/en/stable/scripting-ref.html#splash-go
    -- If not OK, but HTTP error, we want to wait. Otherwise, we still want to return whatever we can, but no need to wait.
    -- Note that the errors will only concern the main webpage and redirects, not any of the resources.
    if ok or reason:find('^http') then
        if ok then
            err = nil
        else
            err = reason
        end
        splash:wait{args.wait}

        splash:set_viewport_full()

        -- Page instrumentation
        splash.scroll_position = {y=1000}

        splash:wait{args.wait}
    else
        err = reason
    end

    -- Response
    return {
        har = splash:har(),
        html = splash:html(),
        png = splash:png{render_all=true},
        cookies = splash:get_cookies(),
		last_redirected_url = splash:url(),
        error = err
    }
end
