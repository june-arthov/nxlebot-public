#!/usr/bin/env node

/**
 * Project Status Update Script
 * Usage: node update-projects.js [project-id] [status|progress|notes]
 * Examples:
 *   node update-projects.js seo-toolbox progress 95
 *   node update-projects.js ocp-website status completed
 *   node update-projects.js virtual-office-game notes "Added new feature X"
 */

const fs = require('fs');
const path = require('path');

const STATUS_FILE = path.join(__dirname, 'project-status.json');
const MARKDOWN_FILE = path.join(__dirname, 'PROJECTS.md');

function loadProjects() {
  try {
    const data = fs.readFileSync(STATUS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    console.error('Error loading projects:', err.message);
    process.exit(1);
  }
}

function saveProjects(projects) {
  try {
    fs.writeFileSync(STATUS_FILE, JSON.stringify(projects, null, 2), 'utf8');
    console.log('✅ Projects saved successfully');
  } catch (err) {
    console.error('Error saving projects:', err.message);
    process.exit(1);
  }
}

function updateMarkdown(projects) {
  // This would be enhanced to auto-update the markdown file
  console.log('📝 Markdown update: Manual update recommended for now');
}

function showHelp() {
  console.log(`
Project Status Update Script
============================

Usage: node ${path.basename(__filename)} [project-id] [field] [value]

Commands:
  status    - Update project status (active|completed|postponed|archived)
  progress   - Update progress percentage (0-100)
  notes      - Add/update project notes
  add        - Add new project
  list       - List all projects
  help       - Show this help

Examples:
  node ${path.basename(__filename)} seo-toolbox progress 95
  node ${path.basename(__filename)} ocp-website status completed
  node ${path.basename(__filename)} virtual-office-game notes "Added new UI"
  node ${path.basename(__filename)} list
`);
}

function listProjects() {
  const projects = loadProjects();
  
  console.log('\n📋 Current Projects:');
  console.log('='.repeat(60));
  
  Object.values(projects.projects).forEach(project => {
    const statusEmoji = {
      completed: '✅',
      active: '🚧',
      postponed: '⏳',
      archived: '📦'
    }[project.status] || '❓';
    
    console.log(`${statusEmoji} ${project.name}`);
    console.log(`   Status: ${project.status} (${project.progress}%)`);
    console.log(`   Priority: ${project.priority}`);
    console.log(`   Location: ${project.location}`);
    console.log(`   Last Updated: ${project.lastUpdated || 'N/A'}`);
    if (project.notes) {
      console.log(`   Notes: ${project.notes}`);
    }
    if (project.blockers && project.blockers.length > 0) {
      console.log(`   ⚠️  Blockers: ${project.blockers.join(', ')}`);
    }
    console.log('');
  });
  
  console.log('📊 Summary:');
  console.log(`   Total Projects: ${projects.stats.totalProjects}`);
  console.log(`   Completed: ${projects.stats.completed}`);
  console.log(`   Active: ${projects.stats.active}`);
  console.log(`   Postponed: ${projects.stats.postponed}`);
  console.log(`   Archived: ${projects.stats.archived}`);
}

function addProject() {
  // This would be enhanced with interactive prompts
  console.log('➕ Add project: Feature coming soon');
}

function updateProject(projectId, field, value) {
  const projects = loadProjects();
  
  if (!projects.projects[projectId]) {
    console.error(`❌ Project "${projectId}" not found`);
    console.log('\nAvailable projects:');
    Object.keys(projects.projects).forEach(id => console.log(`  - ${id}`));
    process.exit(1);
  }
  
  const project = projects.projects[projectId];
  const oldValue = project[field];
  
  // Validate and update
  if (field === 'status') {
    const validStatuses = ['active', 'completed', 'postponed', 'archived'];
    if (!validStatuses.includes(value)) {
      console.error(`❌ Invalid status. Use: ${validStatuses.join(', ')}`);
      process.exit(1);
    }
    project.status = value;
    project.lastUpdated = new Date().toISOString().split('T')[0];
    
  } else if (field === 'progress') {
    const progress = parseInt(value);
    if (isNaN(progress) || progress < 0 || progress > 100) {
      console.error('❌ Progress must be 0-100');
      process.exit(1);
    }
    project.progress = progress;
    project.lastUpdated = new Date().toISOString().split('T')[0];
    
  } else if (field === 'notes') {
    project.notes = value;
    project.lastUpdated = new Date().toISOString().split('T')[0];
    
  } else {
    console.error(`❌ Unknown field: ${field}`);
    process.exit(1);
  }
  
  // Update stats
  projects.stats.lastUpdated = new Date().toISOString().split('T')[0];
  
  saveProjects(projects);
  updateMarkdown(projects);
  
  console.log(`✅ Updated ${projectId}.${field}:`);
  console.log(`   Old: ${oldValue}`);
  console.log(`   New: ${project[field]}`);
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === 'help' || args[0] === '--help') {
  showHelp();
} else if (args[0] === 'list') {
  listProjects();
} else if (args[0] === 'add') {
  addProject();
} else if (args.length >= 3) {
  updateProject(args[0], args[1], args.slice(2).join(' '));
} else {
  showHelp();
}