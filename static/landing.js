import { buildLandingCase } from './landing-case.js';

const story = buildLandingCase();
const scenes = [...document.querySelectorAll('[data-scene]')];
const chapters = [...document.querySelectorAll('[data-step]')];
const chapterIds = chapters.map((chapter) => chapter.dataset.chapterId);
const links = [...document.querySelectorAll('.chapter-nav a')];
const percent = (value) => `${Math.round(value * 100)}%`;

for (const [selector, value] of [
  ['[data-initial-prob]', story.initialSignals.route.ecu_comm],
  ['[data-initial-suff]', story.initialSignals.sufficient],
  ['[data-before]', story.initialSignals.route.ecu_comm],
  ['[data-after]', story.finalSignals.route.ecu_comm],
]) document.querySelector(selector).textContent = percent(value);

document.querySelector('#candidate-list').replaceChildren(...story.initial.candidates.slice(0, 3).map((candidate) => {
  const item = document.createElement('li');
  const name = document.createElement('span');
  const utility = document.createElement('strong');
  name.textContent = candidate.label;
  utility.textContent = new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 3 }).format(candidate.U);
  item.append(name, utility);
  return item;
}));
document.querySelector('#evidence-request').textContent = story.initial.candidates[0].label;
document.querySelector('#route-target').textContent = story.final.target_label;

const riskToggle = document.querySelector('#risk-toggle');
riskToggle.disabled = false;
riskToggle.addEventListener('click', () => {
  const active = riskToggle.getAttribute('aria-pressed') !== 'true';
  riskToggle.setAttribute('aria-pressed', String(active));
  scenes[5].classList.toggle('is-critical', active);
  document.querySelector('#safety-title').innerHTML = active ? 'Otomasyon durur.<br>İnsan devreye girer.' : 'Aynı vaka.<br>Yeni bir risk.';
  document.querySelector('#safety-explanation').textContent = active ? 'Güvenlik kapısı ilk notta tetiklendi. Jev çağrısına gerek yok.' : 'İlk notta yanık kokusu olsaydı ne değişirdi?';
  const result = document.querySelector('#safety-result');
  result.textContent = active ? `ESCALATE · ${story.critical.target_label}` : 'Güvenlik kapısını denemek için notu değiştir.';
  result.dataset.action = active ? story.critical.action : '';
});

function readingMode(enabled) {
  scenes.forEach((scene, index) => {
    scene.id = enabled ? chapterIds[index] : '';
    chapters[index].id = enabled ? '' : chapterIds[index];
  });
}
readingMode(true);

// The only clock is GSAP's ticker; no second RAF loop or touch-scroll hijack.
if (window.gsap && window.ScrollTrigger && window.Lenis) {
  const { gsap, ScrollTrigger, Lenis } = window;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add('(prefers-reduced-motion: no-preference) and (min-height: 800px)', () => {
    readingMode(false);
    document.body.classList.add('motion');
    const lenis = new Lenis({ duration: 1.05, autoRaf: false, syncTouch: false, anchors: true });
    const tick = (seconds) => lenis.raf(seconds * 1000);
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    gsap.set(scenes, { autoAlpha: 0 });
    gsap.set(scenes[0], { autoAlpha: 1 });
    let current = 0;
    const timeline = gsap.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: {
        trigger: '#story', start: 'top top', end: 'bottom bottom', scrub: 0.35,
        onUpdate: ({ progress }) => {
          const next = Math.min(5, Math.round(progress * 5));
          if (next === current) return;
          current = next;
          links.forEach((link, index) => {
            if (index === next) link.setAttribute('aria-current', 'step');
            else link.removeAttribute('aria-current');
          });
        },
      },
    });
    // Evidence packets converge; then the same scroll reveals the policy and result.
    timeline.to('.source-note', { x: 55, rotation: 0, scale: 0.9, duration: 0.7 }, 0);
    timeline.to('.dtc-source', { x: -30, rotation: 0, duration: 0.7 }, 0);
    timeline.to('.history-source', { x: 25, duration: 0.7 }, 0);
    for (let index = 1; index < scenes.length; index++) {
      timeline.to(scenes[index - 1], { autoAlpha: 0, y: -25, duration: 0.22 }, index - 0.42);
      timeline.fromTo(scenes[index], { y: 35, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.28 }, index - 0.31);
    }
    timeline.from('.signal-track i', { scaleX: 0, stagger: 0.06, duration: 0.35 }, 0.45);
    timeline.from('.candidate-list li', { x: 35, stagger: 0.07, duration: 0.35 }, 1.5);
    timeline.from('.measurement>strong', { clipPath: 'inset(100% 0 0 0)', y: 30, duration: 0.4 }, 2.55);
    timeline.from('.circuit', { scaleX: 0.7, transformOrigin: 'left', duration: 0.4 }, 2.55);
    timeline.from('.handoff-packet>div>span', { autoAlpha: 0, y: 12, stagger: 0.05, duration: 0.25 }, 3.5);
    timeline.to('.story-progress i', { scaleX: 1, duration: 5 }, 0);
    timeline.to({}, { duration: 0.01 }, 4.99);
    const hero = gsap.to('.hero-vehicle', {
      yPercent: 12, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
    const refresh = () => ScrollTrigger.refresh();
    document.fonts.ready.then(refresh);
    window.addEventListener('load', refresh, { once: true });
    // Native scrolling and every scene return when the user changes motion preference.
    return () => {
      window.removeEventListener('load', refresh);
      gsap.ticker.remove(tick);
      lenis.destroy();
      hero.kill();
      document.body.classList.remove('motion');
      readingMode(true);
    };
  });
}
