import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import vm from 'node:vm';

async function loadApi(fetchImpl) {
    const source = await readFile(new URL('../assets/js/api.js', import.meta.url), 'utf8');
    const sandbox = {
        console,
        fetch: fetchImpl,
        localStorage: { getItem: () => null, removeItem: () => {} },
        document: { addEventListener: () => {} },
        window: { location: { href: '' } },
        alert: () => {},
    };
    vm.runInNewContext(`${source}\nglobalThis.__api = api;`, sandbox);
    return sandbox.__api;
}

test('getAll unwraps and follows paginated responses', async () => {
    const requests = [];
    const api = await loadApi(async (url) => {
        requests.push(url);
        const page = new URL(url, 'https://example.test').searchParams.get('page');
        const body = page === '1'
            ? { success: true, data: [{ id: 1 }], pagination: { page: 1, has_next: true } }
            : { success: true, data: [{ id: 2 }], pagination: { page: 2, has_next: false } };
        return { ok: true, async json() { return body; } };
    });

    const result = await api.classification.getAll();

    assert.deepEqual(result, [{ id: 1 }, { id: 2 }]);
    assert.equal(requests.length, 2);
    assert.match(requests[0], /page=1&per_page=100/);
    assert.match(requests[1], /page=2&per_page=100/);
});

test('getAll keeps compatibility with legacy array responses', async () => {
    const api = await loadApi(async () => ({
        ok: true,
        async json() { return [{ id: 1 }, { id: 2 }]; },
    }));

    assert.deepEqual(await api.teacher.getAll(), [{ id: 1 }, { id: 2 }]);
});
