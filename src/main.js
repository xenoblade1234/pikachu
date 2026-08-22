import './style.css'

const navToggle = document.getElementById('nav-toggle')
const navLinks = document.getElementById('nav-links')

navToggle.addEventListener('click', () => {
  const open = navLinks.classList.toggle('is-open')
  navToggle.setAttribute('aria-expanded', String(open))
})

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('is-open')
    navToggle.setAttribute('aria-expanded', 'false')
  })
})

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

if (!prefersReducedMotion && 'IntersectionObserver' in window) {
  const revealTargets = document.querySelectorAll(
    '.service-card, .steps li, .testimonials blockquote, .about-grid, .kontakt-grid'
  )

  revealTargets.forEach((el) => el.classList.add('reveal'))

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.2 }
  )

  revealTargets.forEach((el) => observer.observe(el))
}
