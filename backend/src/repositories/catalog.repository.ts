import { pool } from '../config/database';
import { CatalogItem, ItemType } from '../types';

export async function getAllItems(type?: ItemType): Promise<CatalogItem[]> {
  if (type) {
    const { rows } = await pool.query<CatalogItem>(
      'SELECT * FROM catalog_items WHERE active = true AND type = $1 ORDER BY type, name',
      [type]
    );
    return rows;
  }
  const { rows } = await pool.query<CatalogItem>(
    'SELECT * FROM catalog_items WHERE active = true ORDER BY type, name'
  );
  return rows;
}

export async function getItemsByIds(ids: string[]): Promise<CatalogItem[]> {
  if (ids.length === 0) return [];
  const { rows } = await pool.query<CatalogItem>(
    `SELECT * FROM catalog_items
     WHERE id = ANY($1::uuid[]) AND active = true`,
    [ids]
  );
  return rows;
}
