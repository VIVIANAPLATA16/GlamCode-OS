    # ==========================================================
    # SESSION DEBUG TOOLKIT (RENDER SAFE VERSION)
    # ==========================================================
    # Este bloque permite diagnosticar problemas de sesión
    # detrás de proxy HTTPS (Render + Gunicorn).
    #
    # Puede eliminarse después de confirmar que login funciona.
    # ==========================================================

    from flask import request, session, jsonify
    import os

    SESSION_DEBUG = os.getenv("SESSION_DEBUG", "true").lower() == "true"

    # ----------------------------------------------------------
    # LOG COOKIES RECIBIDAS
    # ----------------------------------------------------------
    @app.before_request
    def session_debug_before_request():

        if not SESSION_DEBUG:
            return

        # Ignorar health checks automáticos de Render
        if request.method == "HEAD" and request.path == "/":
            return

        app.logger.info(
            "[SESSION DEBUG][IN] %s %s cookies=%s",
            request.method,
            request.path,
            dict(request.cookies),
        )

    # ----------------------------------------------------------
    # LOG COOKIES ENVIADAS (SET-COOKIE)
    # ----------------------------------------------------------
    @app.after_request
    def session_debug_after_request(response):

        if not SESSION_DEBUG:
            return response

        try:
            cookies = response.headers.getlist("Set-Cookie")

            for cookie in cookies:
                line = cookie if isinstance(cookie, str) else str(cookie)

                if len(line) > 500:
                    line = line[:500] + "..."

                app.logger.info(
                    "[SESSION DEBUG][OUT] Set-Cookie=%s",
                    line,
                )

        except Exception as e:
            app.logger.error(
                "[SESSION DEBUG][ERROR]=%s",
                str(e),
            )

        return response

    # ----------------------------------------------------------
    # ENDPOINT DE DIAGNÓSTICO
    # ----------------------------------------------------------
    @app.route("/session-debug")
    def session_debug():

        return jsonify(
            session_data=dict(session),
            cookies_received=dict(request.cookies),
            is_logged_in=bool(session.get("usuario_id")),
            environment=os.getenv("RENDER", "local"),
        )
