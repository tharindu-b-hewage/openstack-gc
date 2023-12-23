package route_handler

import (
	"net/http"
)

type IdleStatesRoutesHandler struct {
}

func (o *IdleStatesRoutesHandler) ListAvailableIdleStates(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Idle states analysis is yet to be implemented"))
}
