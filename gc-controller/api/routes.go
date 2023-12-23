package api

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/route-handler"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func loadRoutes() *chi.Mux {
	router := chi.NewRouter()
	router.Use(middleware.Logger)

	router.Route("/idle-states", loadIdleStatesRoutes)

	return router
}

func loadIdleStatesRoutes(router chi.Router) {
	idleStatesRoutesHandler := &route_handler.IdleStatesRoutesHandler{}

	router.Get("/", idleStatesRoutesHandler.ListAvailableIdleStates)
}
