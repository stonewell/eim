package main

import (
	"os"

	"github.com/veandco/go-sdl2/sdl"
)

func run() (err error) {
	var window *sdl.Window

	if err = sdl.Init(sdl.INIT_VIDEO); err != nil {
		return
	}
	defer sdl.Quit()

	// Create a window for us to draw the text on
	if window, err = sdl.CreateWindow("Drawing text",
		sdl.WINDOWPOS_UNDEFINED,
		sdl.WINDOWPOS_UNDEFINED,
		800, 600,
		sdl.WINDOW_SHOWN); err != nil {
		return
	}
	defer window.Destroy()

	// Update the window surface with what we have drawn
	window.UpdateSurface()

	// Run infinite loop until user closes the window
	running := true
	for running {
		for event := sdl.PollEvent(); event != nil; event = sdl.PollEvent() {
			switch event.(type) {
			case *sdl.QuitEvent:
				running = false
			}
		}

		sdl.Delay(16)
	}

	return
}

func main() {
	if err := run(); err != nil {
		os.Exit(1)
	}
}
