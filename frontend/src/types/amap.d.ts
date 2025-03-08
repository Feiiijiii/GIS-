declare namespace AMap {
  class Map {
    constructor(container: string | HTMLElement, options: MapOptions)
    destroy(): void
    setMapStyle(style: string): void
    setRotation(rotation: number): void
    setPitch(pitch: number): void
    setViewMode(mode: '2D' | '3D'): void
    setZoomAndCenter(zoom: number, center: [number, number]): void
    addControl(control: any): void
    add(layer: any): void
    remove(overlay: any): void
    setLayers(layers: Layer[]): void
  }

  class Marker {
    constructor(options: MarkerOptions)
    on(event: string, callback: Function): void
    setMap(map: Map | null): void
    remove(): void
    getPosition(): { getLng(): number; getLat(): number }
    getTitle(): string
  }

  class Scale {
    constructor(options?: any)
  }

  class ToolBar {
    constructor(options?: any)
  }

  class MouseTool {
    constructor(map: Map)
    polygon(options?: PolygonOptions): void
    on(event: string, callback: Function): void
    close(clear?: boolean): void
  }

  namespace GeometryUtil {
    function isPointInRing(point: [number, number], ring: any[]): boolean
  }

  class Layer {
    setMap(map: Map | null): void
    remove(): void
  }

  class TileLayer extends Layer {
    constructor(options?: any)
    static Satellite: {
      new(options?: any): TileLayer
    }
    static RoadNet: {
      new(options?: any): TileLayer
    }
  }

  interface MapOptions {
    zoom?: number
    center?: [number, number]
    viewMode?: '2D' | '3D'
    pitch?: number
    rotation?: number
    mapStyle?: string
    features?: string[]
    buildingAnimation?: boolean
    skyColor?: string
    canvas?: {
      willReadFrequently: boolean
    }
    layers?: Layer[]
  }

  interface MarkerOptions {
    position: [number, number]
    title?: string
    label?: {
      content: string
      direction?: string
    }
    icon?: string
  }

  interface PolygonOptions {
    strokeColor?: string
    strokeOpacity?: number
    strokeWeight?: number
    fillColor?: string
    fillOpacity?: number
    strokeStyle?: string
  }
}

declare global {
  interface Window {
    AMap: typeof AMap
  }
} 