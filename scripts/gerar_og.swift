// Gera assets/img/og-mro2027.jpg (1200x630) com a arte do folder e o logotipo novo.
// Uso: swift scripts/gerar_og.swift
import AppKit
let raiz = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
func img(_ p: String) -> CGImage { NSImage(contentsOf: raiz.appendingPathComponent(p))!.cgImage(forProposedRect: nil, context: nil, hints: nil)! }
let W = 1200, H = 630
let cs = CGColorSpaceCreateDeviceRGB()
let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: cs, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
// fundo marinho
ctx.setFillColor(CGColor(red: 0.004, green: 0.027, blue: 0.149, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
// arte do folder, à direita
let arte = img("assets/img/folder-jato.jpg")
let aw = Double(arte.width), ah = Double(arte.height)
let alvoH = Double(H), esc = alvoH / ah
ctx.draw(arte, in: CGRect(x: Double(W) - aw * esc * 0.92, y: 0, width: aw * esc, height: alvoH))
// degradê para dar contraste ao texto
let grad = CGGradient(colorsSpace: cs, colors: [CGColor(red: 0.004, green: 0.027, blue: 0.149, alpha: 1), CGColor(red: 0.004, green: 0.027, blue: 0.149, alpha: 0.92), CGColor(red: 0.004, green: 0.027, blue: 0.149, alpha: 0)] as CFArray, locations: [0, 0.45, 1])!
ctx.drawLinearGradient(grad, start: CGPoint(x: 0, y: 0), end: CGPoint(x: Double(W) * 0.75, y: 0), options: [])
// faixa ciano superior
ctx.setFillColor(CGColor(red: 0, green: 0.694, blue: 0.769, alpha: 1)); ctx.fill(CGRect(x: 0, y: H - 10, width: W, height: 10))
// logotipo branco
let logo = img("assets/img/logo-mro2027-branco.png")
let lw = 430.0, lh = lw * Double(logo.height) / Double(logo.width)
ctx.draw(logo, in: CGRect(x: 64, y: Double(H) - 64 - lh - 10, width: lw, height: lh))
NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
func texto(_ t: String, _ x: Double, _ y: Double, _ tam: CGFloat, _ peso: NSFont.Weight, _ cor: NSColor) {
  NSAttributedString(string: t, attributes: [.font: NSFont.systemFont(ofSize: tam, weight: peso), .foregroundColor: cor]).draw(at: NSPoint(x: x, y: y))
}
// filete vermelho + tema
ctx.setFillColor(CGColor(red: 0.882, green: 0.141, blue: 0.161, alpha: 1)); ctx.fill(CGRect(x: 64, y: 226, width: 56, height: 5))
texto("A INTELIGÊNCIA NA REVOLUÇÃO DO MRO", 64, 190, 22, .regular, .white)
texto("20 e 21 de outubro de 2027", 64, 118, 46, .bold, NSColor(red: 0, green: 0.694, blue: 0.769, alpha: 1))
texto("Centro de Convenções Frei Caneca · São Paulo — SP", 64, 72, 24, .medium, .white)
let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85])!.write(to: raiz.appendingPathComponent("assets/img/og-mro2027.jpg"))
print("og-mro2027.jpg gerada")
