package api

import (
	"context"
	"fmt"
	"net/http"
)

type Service struct {
	router http.Handler
}

func New() *Service {
	service := &Service{
		router: loadRoutes(),
	}
	return service
}

func (a *Service) Start(ctx context.Context) error {
	server := &http.Server{
		Addr:    ":3000",
		Handler: a.router,
	}

	err := server.ListenAndServe()
	if err != nil {
		return fmt.Errorf("failed to start the service: %w", err)
	}

	return nil
}
