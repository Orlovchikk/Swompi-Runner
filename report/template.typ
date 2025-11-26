// Up to Typst 0.13.0 date

/// Heading for structural elements.
/// Centered, preferrably uppercase.
#let struct-heading(body) = {
  show heading: it => align(center, it.body)
  pagebreak(weak: true)
  heading(numbering: none, body)
}

// #let code(content) = {
//   set text(size: 12pt, font: "Courier New")
//   par(content, first-line-indent: 0pt, leading: 12pt)
// }

/// leading &mdash; spacing between all lines
#let template(
  leading: 1.5em,
  fontsize: 12pt,
  doc,
) = {
  let lineheight = 0.65em

  set text(
    font: "Times New Roman",
    size: fontsize,
    lang: "ru",
    hyphenate: false,
  )

  // show raw: r => {
  //     set text(size: 12pt, font: "Courier New")
  //     set par(first-line-indent: 0pt, leading: 12pt)
  // }
  
  show raw.where(block: true): it => [
    #set text(size: 12pt, font: "Courier New")
    #let nlines = it.lines.len()
    #table(columns: (auto, auto), align: (right, left), inset: 0.0em, column-gutter: 0.5em, row-gutter: 19pt, stroke: none,
      ..it.lines.enumerate().map(((i, line)) => (math.mono(text(gray)[#(i + 1)]), line)).flatten()
    )

  ]

  set page(
    paper: "a4",
    margin: (
      top: 2cm,
      bottom: 2cm,
      left: 3cm,
      right: 1.5cm,
    ),
    numbering: "1",
    number-align: center + bottom,
  )

  set par(
    leading: leading,
    spacing: leading,
    first-line-indent: (amount: 1.25cm, all: true),
    justify: true,
  )

  set heading(
    numbering: "1.1",
    hanging-indent: 0pt,
  )

  show heading: set text(size: fontsize, hyphenate: false)

  show heading: it => {
    let content = if it.numbering != none {
      context { counter(heading).display(it.numbering) }
      [ ]
      it.body
    } else {
      it.body
    }
    // v(weak: true, lineheight + leading * 2)
    par(hanging-indent: it.hanging-indent, content)
  }

  set outline.entry(fill: repeat[.])
  set outline(title: [СОДЕРЖАНИЕ])

  show outline: it => context {
    set outline(indent: measure("  ").width)
    show linebreak: "."
    show heading: it => struct-heading(it.body)
    it
  }

  set figure(gap: leading)
  set figure.caption(separator: [ --- ])

  // Display caption even without a name
  show figure.where(caption: none): set figure(caption: [])
  show figure.where(caption: none): set figure.caption(separator: [])

  show figure: it => {
    it
    v(leading)
  }

  // Display listings as images, except they are breakable
  show figure.where(kind: raw): set block(width: 100%, breakable: true)
  show figure.where(kind: raw): set figure(kind: image, supplement: [Рисунок])

  show figure.where(kind: table): set figure.caption(position: top)
  show figure.caption.where(kind: table): align.with(left)

  show figure.where(kind: image): set figure(supplement: [Рисунок])

  set math.equation(numbering: "(1)")

  set list(marker: ([--], [•]))

  // Displaying lists as paragraphs
  show list: it => context {
    let list-counter = counter("list-counter")

    let marker = it.marker
    // Циклично выбираем маркер из списка
    if type(marker) == array {
      let i = calc.rem-euclid(list-counter.get().at(0), marker.len())
      marker = marker.at(i)
    } else if type(marker) == function {
      marker = marker(list-counter.get().at(0))
    }
    list-counter.step()
    for item in it.children {
      block({
        h(it.indent)
        marker
        h(it.body-indent)
        item.body
        parbreak()
      })
    }
    list-counter.update(x => x - 1)
  }

  set enum(
    numbering: (x, ..xs) => {
      if xs.pos().len() > 0 {
        numbering("a.", xs.pos().last())
      } else {
        numbering("1.", x)
      }
    },
  )

  // Displaying enums as paragraphs
  show enum: it => context {
    let enum-counter = counter("enum-counter")

    enum-counter.update((..xs) => xs.pos().slice(0, -1) + (0,))
    let level = enum-counter.get().len()
    for item in it.children {
      block({
        enum-counter.step(level: level)
        context {
          h(it.indent)
          numbering(it.numbering, ..enum-counter.get())
          h(it.body-indent)
          enum-counter.update((..xs) => xs.pos() + (0,))
        }
        item.body
        parbreak()
      })
    }
    enum-counter.update((..xs) => xs.pos().slice(0, -1))
  }

  doc
}
