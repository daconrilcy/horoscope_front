import { describe, it, expect } from 'vitest';
import { sanitizeLegalHtml } from './sanitizeLegalHtml';

describe('sanitizeLegalHtml', () => {
  it('devrait retourner une chaîne vide si input est vide', () => {
    expect(sanitizeLegalHtml('')).toBe('');
    expect(sanitizeLegalHtml('   ')).toBe('   ');
  });

  it('devrait retourner une chaîne vide si input est null ou undefined', () => {
    expect(sanitizeLegalHtml(null as unknown as string)).toBe('');
    expect(sanitizeLegalHtml(undefined as unknown as string)).toBe('');
  });

  it("devrait retourner le HTML inchangé si pas d'éléments dangereux", () => {
    const safe = '<div><p>Contenu sécurisé</p></div>';
    expect(sanitizeLegalHtml(safe)).toBe(safe);
  });

  describe('retrait des scripts', () => {
    it('devrait retirer les scripts inline', () => {
      const html = '<div><script>alert("xss")</script><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les scripts externes', () => {
      const html =
        '<div><script src="https://evil.com/script.js"></script><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les scripts avec attributs', () => {
      const html =
        '<div><script type="text/javascript" async>alert("xss")</script><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les scripts avec contenu multiligne', () => {
      const html = `<div>
        <script>
          alert("xss");
          console.log("hack");
        </script>
        <p>Text</p>
      </div>`;
      expect(sanitizeLegalHtml(html)).toContain('<p>Text</p>');
      expect(sanitizeLegalHtml(html)).not.toContain('<script>');
    });
  });

  describe('retrait des iframes, objects, embeds', () => {
    it('devrait retirer les iframes', () => {
      const html =
        '<div><iframe src="https://evil.com"></iframe><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les objects', () => {
      const html =
        '<div><object data="https://evil.com/plugin.swf"></object><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les embeds', () => {
      const html =
        '<div><embed src="https://evil.com/video.swf"></embed><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les balises fermantes iframe/object/embed', () => {
      const html = '<div><iframe src="test"></iframe></div><p>Text</p>';
      expect(sanitizeLegalHtml(html)).toBe('<div></div><p>Text</p>');
    });
  });

  describe('retrait des liens CSS externes', () => {
    it('devrait retirer les liens stylesheet', () => {
      const html =
        '<div><link rel="stylesheet" href="https://evil.com/style.css"><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les liens stylesheet avec guillemets simples', () => {
      const html =
        "<div><link rel='stylesheet' href='https://evil.com/style.css'><p>Text</p></div>";
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });

    it('devrait retirer les liens stylesheet sans guillemets', () => {
      const html =
        '<div><link rel=stylesheet href=https://evil.com/style.css><p>Text</p></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><p>Text</p></div>');
    });
  });

  describe('retrait des attributs on*', () => {
    it('devrait retirer onclick', () => {
      const html = '<div><button onclick="alert(\'xss\')">Click</button></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><button>Click</button></div>');
    });

    it('devrait retirer onload', () => {
      const html = '<div><img onload="alert(\'xss\')" src="test.jpg"></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><img src="test.jpg"></div>');
    });

    it('devrait retirer onerror', () => {
      const html = '<div><img onerror="alert(\'xss\')" src="test.jpg"></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><img src="test.jpg"></div>');
    });

    it('devrait retirer onmouseover', () => {
      const html = '<div><span onmouseover="alert(\'xss\')">Hover</span></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><span>Hover</span></div>');
    });

    it('devrait retirer plusieurs attributs on*', () => {
      const html =
        '<div><button onclick="do1()" onload="do2()" onerror="do3()">Click</button></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><button>Click</button></div>');
    });

    it('devrait retirer les attributs on* avec guillemets simples', () => {
      const html = '<div><button onclick=\'alert("xss")\'>Click</button></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><button>Click</button></div>');
    });
  });

  describe('neutralisation de javascript:', () => {
    it('devrait neutraliser javascript: dans href', () => {
      const html = '<div><a href="javascript:alert(\'xss\')">Link</a></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><a href="#">Link</a></div>');
    });

    it('devrait neutraliser javascript: dans href avec guillemets simples', () => {
      const html = '<div><a href=\'javascript:alert("xss")\'>Link</a></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><a href="#">Link</a></div>');
    });

    it('devrait neutraliser javascript: dans src', () => {
      const html = '<div><img src="javascript:alert(\'xss\')"></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><img src="#"></div>');
    });

    it('devrait neutraliser javascript: avec espaces', () => {
      const html =
        '<div><a href="javascript: void(0); alert(\'xss\')">Link</a></div>';
      expect(sanitizeLegalHtml(html)).toBe('<div><a href="#">Link</a></div>');
    });
  });

  describe('cas complexes', () => {
    it('devrait gérer plusieurs éléments dangereux en même temps', () => {
      const html = `<div>
        <script>alert('xss')</script>
        <iframe src="evil.com"></iframe>
        <button onclick="doSomething()">Click</button>
        <a href="javascript:alert('xss')">Link</a>
        <p>Safe content</p>
      </div>`;
      const sanitized = sanitizeLegalHtml(html);
      expect(sanitized).toContain('<p>Safe content</p>');
      expect(sanitized).toContain('<button>Click</button>');
      expect(sanitized).toContain('<a href="#">Link</a>');
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('<iframe>');
      expect(sanitized).not.toContain('onclick');
      expect(sanitized).not.toContain('javascript:');
    });

    it('devrait préserver le HTML valide et sécurisé', () => {
      const html = `<article>
        <h1>Titre</h1>
        <p>Paragraphe avec <strong>gras</strong> et <em>italique</em>.</p>
        <ul>
          <li>Item 1</li>
          <li>Item 2</li>
        </ul>
        <a href="https://example.com" target="_blank">Lien externe</a>
      </article>`;
      const sanitized = sanitizeLegalHtml(html);
      expect(sanitized).toBe(html);
    });
  });
});
