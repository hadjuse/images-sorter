import { render, screen } from '@testing-library/react';
import ImageUploader from '../src/components/ImageUploader';
import FolderProcessor from '../src/components/FolderProcessor';

describe('Frontend Components - Basic Rendering', () => {
  beforeEach(() => {
    // Mock fetch before each test
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('ImageUploader', () => {
    it('renders without crashing', () => {
      render(<ImageUploader />);
      expect(screen.getByText(/Drop an image here or click to select/i)).toBeInTheDocument();
    });

    it('shows file input', () => {
      render(<ImageUploader />);
      const input = document.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('accept', 'image/*');
    });

    it('displays file type information', () => {
      render(<ImageUploader />);
      expect(screen.getByText(/Supports: JPG, PNG, GIF, WebP, HEIC/i)).toBeInTheDocument();
    });
  });

  describe('FolderProcessor', () => {
    it('renders with default configuration', () => {
      render(<FolderProcessor />);
      expect(screen.getByLabelText(/Folder Path/i)).toBeInTheDocument();
    });

    it('has correct default folder path', () => {
      render(<FolderProcessor />);
      const input = screen.getByDisplayValue('/mnt/c/Users/pc/Pictures/ted/');
      expect(input).toBeInTheDocument();
    });

    it('has correct default extension', () => {
      render(<FolderProcessor />);
      const select = screen.getByRole('combobox', { name: /file extension/i });
      expect(select).toBeInTheDocument();
      expect(select).toHaveValue('png');
    });

    it('shows preview and process buttons', () => {
      render(<FolderProcessor />);
      expect(screen.getByText(/Preview Images/i)).toBeInTheDocument();
      expect(screen.getByText(/Process Folder/i)).toBeInTheDocument();
    });

    it('has max images input with default value', () => {
      render(<FolderProcessor />);
      const input = screen.getByDisplayValue('7');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'number');
    });
  });

  describe('API Configuration', () => {
    it('imports API_BASE_URL from config', async () => {
      const { API_BASE_URL } = await import('../src/config/api');
      expect(API_BASE_URL).toBeDefined();
      expect(typeof API_BASE_URL).toBe('string');
      expect(API_BASE_URL).toContain('127.0.0.1:8000');
    });
  });
});
