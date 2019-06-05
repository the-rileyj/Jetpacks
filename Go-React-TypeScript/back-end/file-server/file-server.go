package main

import (
	"flag"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/the-rileyj/serverutils"
)

func main() {
	debug := flag.Bool("d", false, "Sets debugging mode, Cross-Origin Resource Sharing policy won't discriminate against the request origin (\"Access-Control-Allow-Origin\" header is \"*\")")
	port := ":80"

	flag.Parse()

	router := gin.Default()

	if *debug {
		port = ":9001"

		router.Use(serverutils.HandleCrossOriginResourceSharing)
	}

	router.Any("/api/*path", serverutils.HandleRouteProxying)

	router.GET("/hello-world", func(c *gin.Context) { c.Writer.Write([]byte("HELLO WORLD!")) })

	router.NoRoute(serverutils.HandleReactFileServing("/static"))

	log.Fatal(router.Run(port))
}
