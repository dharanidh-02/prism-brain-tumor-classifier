import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function NavigationTile({
  title,
  description,
  to,
  icon: Icon,
  iconBg = 'var(--prism-indigo-subtle)',
  iconColor = 'var(--prism-indigo)',
}) {
  return (
    <Link to={to} className="nav-tile" aria-label={`Navigate to ${title}`}>
      <div className="nav-tile-left">
        <div className="tile-icon-box" style={{ backgroundColor: iconBg, color: iconColor }}>
          <Icon size={24} />
        </div>
        <div>
          <div className="tile-title">{title}</div>
          <div className="tile-desc">{description}</div>
        </div>
      </div>
      <div style={{ color: 'var(--prism-muted)', display: 'flex', alignItems: 'center' }}>
        <ArrowRight size={18} />
      </div>
    </Link>
  );
}
