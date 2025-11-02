import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useTitle } from './useTitle';

describe('useTitle', () => {
  const originalTitle = document.title;

  beforeEach(() => {
    document.title = '';
  });

  afterEach(() => {
    document.title = originalTitle;
    vi.clearAllMocks();
  });

  it('devrait mettre à jour document.title', () => {
    renderHook(() => useTitle('Test Title'));
    expect(document.title).toBe('Test Title');
  });

  it('devrait mettre à jour document.title quand le titre change', () => {
    const { rerender } = renderHook(({ title }) => useTitle(title), {
      initialProps: { title: 'First Title' },
    });
    expect(document.title).toBe('First Title');

    rerender({ title: 'Second Title' });
    expect(document.title).toBe('Second Title');
  });
});

