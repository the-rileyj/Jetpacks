package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/the-rileyj/serverutils"
)

func main() {
	port := ":80"
	router := gin.Default()

	apiNoAuth := router.Group("/api")
	apiNoAuth.GET("/hello-world", func(c *gin.Context) { c.Writer.Write([]byte("HELLO WORLD!")) })

	apiAuth := router.Group("/api")
	apiAuth.Use(serverutils.HandleCheckingAuth(func(c *gin.Context) bool { return false }))

	log.Fatal(router.Run(port))
}
