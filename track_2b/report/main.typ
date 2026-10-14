#import "apertool.typ": report

#show: report.with(
  title: "Inbrev",
  subtitle: "Sovereign inbox triage for Swiss medical practices",
  track: "Track 2B — Own Project",
  authors: ((name: "Niklas Wichter"),),
)

#show figure.where(kind: table): set figure(placement: auto, scope: "parent")

#include "body.typ"

= References
#bibliography("refs.bib", style: "apa")
