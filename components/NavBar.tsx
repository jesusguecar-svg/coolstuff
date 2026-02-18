import Link from 'next/link';

const links = [
  ['/', 'Home'],
  ['/catalog', 'Catalog'],
  ['/phrases', 'Phrases'],
  ['/learn', 'Learn'],
  ['/profile', 'Profile'],
  ['/admin', 'Admin']
];

export function NavBar() {
  return (
    <nav className="flex flex-wrap gap-3 text-sm">
      {links.map(([href, label]) => (
        <Link key={href} href={href} className="rounded-md bg-slate-800 px-3 py-1 hover:bg-slate-700">
          {label}
        </Link>
      ))}
    </nav>
  );
}
