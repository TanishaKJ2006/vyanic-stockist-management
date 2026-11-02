const iconPaths = {
  dashboard: (
    <>
      <rect x="3.5" y="3.5" width="7" height="7" rx="1.7" />
      <rect x="13.5" y="3.5" width="7" height="4.5" rx="1.7" />
      <rect x="13.5" y="11" width="7" height="9.5" rx="1.7" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1.7" />
    </>
  ),
  products: (
    <>
      <path d="m12 3 8.2 4.5v9L12 21l-8.2-4.5v-9L12 3Z" />
      <path d="m3.8 7.5 8.2 4.7 8.2-4.7M12 12.2V21m-4.2-15.9 8.3 4.7" />
    </>
  ),
  stockists: (
    <>
      <path d="M3.5 20.5h17M5.5 20.5V7.8L12 4l6.5 3.8v12.7" />
      <path d="M9 10.1h.1m5.8 0h.1M9 13.8h.1m5.8 0h.1M10 20.5v-3.8h4v3.8" />
    </>
  ),
  audit: (
    <>
      <path d="M12 8v4.5l3 1.8" />
      <circle cx="12" cy="12" r="8.7" />
      <path d="M4.1 5.8 2.8 9m1.3-3.2 3.3.7" />
    </>
  ),
  menu: (
    <>
      <path d="M4 7h16M4 12h16M4 17h16" />
    </>
  ),
  close: <path d="m6 6 12 12M18 6 6 18" />,
  logout: (
    <>
      <path d="M10 17l5-5-5-5m5 5H3" />
      <path d="M12 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5" />
    </>
  ),
  calendar: (
    <>
      <rect x="3.5" y="5" width="17" height="15.5" rx="2.2" />
      <path d="M7.5 3.5v3M16.5 3.5v3M3.5 9.5h17" />
    </>
  ),
  activity: (
    <>
      <path d="M3 12h4l2.2-6 4 12 2.3-6H21" />
    </>
  ),
  server: (
    <>
      <rect x="3.5" y="4" width="17" height="6.5" rx="2" />
      <rect x="3.5" y="13.5" width="17" height="6.5" rx="2" />
      <path d="M7.5 7.2h.1m-.1 9.5h.1m4-.1h5" />
    </>
  ),
  arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
  empty: (
    <>
      <path d="M5 8.5h14l1.5 11h-17L5 8.5Z" />
      <path d="m5 8.5 2.2-4h9.6l2.2 4M9 12.5h6" />
    </>
  ),
  sparkle: (
    <>
      <path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" />
      <path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15Z" />
    </>
  ),
  plus: <path d="M12 5v14m-7-7h14" />,
  search: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></>,
  edit: <><path d="m4 16.5-.8 4.3 4.3-.8L20 7.5 16.5 4 4 16.5Z" /><path d="m14.8 5.7 3.5 3.5" /></>,
  trash: <><path d="M4 7h16M10 11v6m4-6v6M5.5 7l1 13h11l1-13M9 7V4h6v3" /></>,
  chevron: <path d="m6 9 6 6 6-6" />,
  warning: <><path d="m12 3 9 16H3l9-16Z" /><path d="M12 9v4m0 3h.01" /></>,
  shield: <><path d="M12 3 20 6v5c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V6l8-3Z" /><path d="m9 12 2 2 4-4" /></>,
};

export default function Icon({ name, size = 20, strokeWidth = 1.7, className = "" }) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {iconPaths[name] ?? iconPaths.sparkle}
    </svg>
  );
}
